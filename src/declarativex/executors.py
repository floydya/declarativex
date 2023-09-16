# pylint: disable=invalid-overridden-method
import abc
import asyncio
import inspect
import threading
from asyncio import (
    wait_for,
    CancelledError,
    TimeoutError as AsyncioTimeoutError,
)
from queue import Empty, Queue
from typing import Any, Callable, Dict, Optional, Tuple

import httpx

from . import BaseClient
from .exceptions import HTTPException, TimeoutException, MisconfiguredException
from .models import (
    EndpointConfiguration,
    ClientConfiguration,
    RawRequest,
    Response,
)
from .utils import ReturnType

# Check if h2 is installed to enable http2 support
try:  # pragma: no cover
    import h2  # type: ignore[import]
except ImportError:  # pragma: no cover
    h2 = None


class Executor(abc.ABC):
    raw_request: RawRequest
    _func: Callable

    def __init__(self, endpoint_configuration: EndpointConfiguration):
        self.endpoint_configuration = endpoint_configuration

    @property
    def func(self) -> Callable:
        return self._func

    @func.setter
    def func(self, func: Callable) -> None:
        for middleware in self._middlewares:
            is_async = asyncio.iscoroutinefunction(func)
            if getattr(middleware, "_async") is not is_async:
                mw_type = ["sync", "async"]
                raise MisconfiguredException(
                    f"Cannot use {mw_type[not is_async]} middleware"
                    f"({middleware.__class__.__name__}) with "
                    f"{mw_type[is_async]} function"
                )

        self._func = func

    def merge_args_and_kwargs(
        self, *args, **kwargs
    ) -> Tuple[Dict[str, Any], Optional[BaseClient], Optional[BaseClient]]:
        """
        This method is used to merge args and kwargs into a single kwargs
        dictionary. It also returns the self and cls objects if they are
        present in the kwargs.
        """
        signature = inspect.signature(self.func)
        param_names = list(signature.parameters.keys())
        kwargs.update(dict(zip(param_names, args)))
        # Remove self and cls from kwargs, it will be used
        # later to get and update the client configuration
        self_, cls_ = kwargs.pop("self", None), kwargs.pop("cls", None)
        return kwargs, self_, cls_

    @abc.abstractmethod
    def wait_for(self, client, request: httpx.Request):
        """
        This method is used to wait for a function to finish, especially
        for timeout handling.
        """
        raise NotImplementedError

    def update_configuration(
        self, self_: Optional[BaseClient], cls_: Optional[BaseClient]
    ) -> None:
        """
        This method is used to update the client configuration with the
        configuration from the self and cls objects.
        If the self or cls objects are not present, this method does nothing.
        """
        class_config = ClientConfiguration.extract_from_func_kwargs(
            self_=self_, cls_=cls_
        )
        if class_config:
            client_configuration = (
                self.endpoint_configuration.client_configuration.merge(
                    class_config
                )
            )
            self.endpoint_configuration.client_configuration = (
                client_configuration
            )

    def prepare_request(self, **kwargs) -> None:
        """
        This method is used to prepare the raw request.
        It also applies the middlewares to the raw request.
        """
        self.raw_request = RawRequest.initialize(
            self.endpoint_configuration
        ).prepare(self.func, **kwargs)

    def parse_response(
        self,
        httpx_request: httpx.Request,
        httpx_response: httpx.Response,
    ):
        """
        This method is used to parse the httpx response into the
        return type of the function.
        It also applies the middlewares to the response.
        """
        try:
            return Response(response=httpx_response).as_type_for_func(
                self.func
            )
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                request=httpx_request,
                response=httpx_response,
                raw_request=self.raw_request,
                error_mappings=self._error_mappings,
            ) from e

    def _chain_middlewares(
        self, execute: Callable[[RawRequest], ReturnType]
    ) -> ReturnType:
        """
        This method is used to chain the middlewares together. It uses
        recursion to chain them together. The last middleware will call
        the execute function.
        """
        execute_func = execute
        for mw in reversed(self._middlewares):

            def wrap(middleware, prev_func):
                def _wrapped(request: RawRequest):
                    return middleware(request=request, call_next=prev_func)

                return _wrapped

            execute_func = wrap(mw, execute_func)
        return execute_func(self.raw_request)

    def execute(self, func, *args, **kwargs):
        self.func = func
        kwargs, self_, cls_ = self.merge_args_and_kwargs(*args, **kwargs)
        self.update_configuration(self_, cls_)
        self.prepare_request(**kwargs)
        if self._middlewares:
            return self._chain_middlewares(self._execute)
        return self._execute(self.raw_request)

    @abc.abstractmethod
    def _execute(self, request: RawRequest):
        raise NotImplementedError

    @property
    def _error_mappings(self):
        """
        This property is used to get the error mappings from the client
        configuration.
        """
        return self.endpoint_configuration.client_configuration.error_mappings

    @property
    def _middlewares(self):
        """
        This property is used to get the middlewares from the client
        configuration.
        """
        return self.endpoint_configuration.client_configuration.middlewares


class AsyncExecutor(Executor):
    async def wait_for(
        self, client: httpx.AsyncClient, request: httpx.Request
    ):
        """
        This method is used to wait for a function to finish, especially
        for timeout handling. It uses asyncio.wait_for to wait for the
        function to finish. Due to httpx timeouts not working properly,
        this method is used to handle it.
        """
        timeout = (
            self.raw_request.timeout or self.endpoint_configuration.timeout
        )

        if timeout:
            try:
                return await wait_for(
                    client.send(request),
                    timeout=timeout,
                )
            except (TimeoutError, CancelledError, AsyncioTimeoutError) as e:
                raise TimeoutException(
                    timeout=timeout,
                    request=request,
                ) from e
        return await client.send(request)

    async def _execute(self, request: RawRequest):
        async with httpx.AsyncClient(
            follow_redirects=True, http2=bool(h2)
        ) as client:
            httpx_request = request.to_httpx_request()
            httpx_response = await self.wait_for(
                client=client, request=httpx_request
            )
            return self.parse_response(
                httpx_request=httpx_request,
                httpx_response=httpx_response,
            )


class SyncExecutor(Executor):
    def wait_for(self, client: httpx.Client, request: httpx.Request):
        """
        This method is used to wait for a function to finish, especially
        for timeout handling. It uses threading to wait for the function
        to finish. Due to httpx timeouts not working properly, this
        method is used to handle it.
        """
        timeout = (
            self.raw_request.timeout or self.endpoint_configuration.timeout
        )

        if timeout:
            queue: Queue = Queue()

            def wrapper():
                result = client.send(request)
                queue.put(result)

            thread = threading.Thread(target=wrapper)
            thread.start()

            try:
                return queue.get(timeout=timeout)
            except Empty:
                thread.join()
                raise TimeoutException(
                    timeout=timeout,
                    request=request,
                )
        return client.send(request)

    def _execute(self, request: RawRequest):
        with httpx.Client(
            follow_redirects=True, http2=bool(h2)
        ) as client:
            httpx_request = request.to_httpx_request()
            httpx_response = self.wait_for(
                client=client, request=httpx_request
            )
            return self.parse_response(
                httpx_request=httpx_request,
                httpx_response=httpx_response,
            )
