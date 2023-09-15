# pylint: disable=invalid-overridden-method
import abc
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


class Executor(abc.ABC):
    raw_request: RawRequest

    def __init__(self, endpoint_configuration: EndpointConfiguration):
        self.endpoint_configuration = endpoint_configuration

    @staticmethod
    def merge_args_and_kwargs(
        func, *args, **kwargs
    ) -> Tuple[Dict[str, Any], Optional[BaseClient], Optional[BaseClient]]:
        """
        This method is used to merge args and kwargs into a single kwargs
        dictionary. It also returns the self and cls objects if they are
        present in the kwargs.
        """
        signature = inspect.signature(func)
        param_names = list(signature.parameters.keys())
        kwargs.update(dict(zip(param_names, args)))
        # Remove self and cls from kwargs, it will be used
        # later to get and update the client configuration
        self_, cls_ = kwargs.pop("self", None), kwargs.pop("cls", None)
        return kwargs, self_, cls_

    @abc.abstractmethod
    def wait_for(self, func: Callable, request: httpx.Request):
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

    @abc.abstractmethod
    def apply_request_middlewares(self, func, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def apply_response_middlewares(self, response):
        raise NotImplementedError

    def prepare_request(self, func, **kwargs) -> None:
        """
        This method is used to prepare the raw request.
        It also applies the middlewares to the raw request.
        """
        self.raw_request = RawRequest.initialize(
            self.endpoint_configuration
        ).prepare(func, **kwargs)

    def parse_response(
        self,
        func: Callable[..., ReturnType],
        httpx_request: httpx.Request,
        httpx_response: httpx.Response,
    ) -> ReturnType:
        """
        This method is used to parse the httpx response into the
        return type of the function.
        It also applies the middlewares to the response.
        """
        try:
            return Response(response=httpx_response).as_type_for_func(func)
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                request=httpx_request,
                response=httpx_response,
                raw_request=self.raw_request,
                error_mappings=self._error_mappings,
            ) from e

    def execute(self, func, *args, **kwargs):
        return self._execute(func, *args, **kwargs)

    @abc.abstractmethod
    def _execute(self, func, *args, **kwargs):
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
    async def wait_for(self, func: Callable, request: httpx.Request):
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
                    func(request),
                    timeout=timeout,
                )
            except (TimeoutError, CancelledError, AsyncioTimeoutError) as e:
                raise TimeoutException(
                    timeout=timeout,
                    request=request,
                ) from e
        return await func(request)

    async def apply_request_middlewares(self, func, **kwargs) -> None:
        for middleware in self._middlewares:
            # Set function to be used in middleware
            middleware.set_func(func)

            # Modify raw request
            self.raw_request = await middleware.modify_request(
                self.raw_request
            )

            # If the result of .modify_request() is not a RawRequest,
            # raise an exception
            if not isinstance(self.raw_request, RawRequest):
                raise MisconfiguredException(
                    f"{middleware.__class__.__name__}.modify_request "
                    "must return a RawRequest"
                )

    async def apply_response_middlewares(self, response) -> Any:
        for middleware in self._middlewares:
            response = await middleware.modify_response(response)
            # If the result of .modify_response() is not a Response,
            # don't care about it. It's not the middlewares fault
            # if the user doesn't know what they're doing.
        return response

    async def _execute(self, func, *args, **kwargs):
        kwargs, self_, cls_ = self.merge_args_and_kwargs(func, *args, **kwargs)
        self.update_configuration(self_, cls_)
        self.prepare_request(func, **kwargs)
        await self.apply_request_middlewares(func, **kwargs)
        async with httpx.AsyncClient(follow_redirects=True) as client:
            httpx_request = self.raw_request.to_httpx_request()
            httpx_response = await self.wait_for(
                func=client.send, request=httpx_request
            )
            response = self.parse_response(
                func=func,
                httpx_request=httpx_request,
                httpx_response=httpx_response,
            )
            return await self.apply_response_middlewares(response)


class SyncExecutor(Executor):
    def wait_for(self, func: Callable, request: httpx.Request):
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
                result = func(request)
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
        return func(request)

    def apply_request_middlewares(self, func, **kwargs) -> None:
        for middleware in self._middlewares:
            # Set function to be used in middleware
            middleware.set_func(func)

            # Modify raw request
            self.raw_request = middleware.modify_request(self.raw_request)

            # If the result of .modify_request() is not a RawRequest,
            # raise an exception
            if not isinstance(self.raw_request, RawRequest):
                raise MisconfiguredException(
                    f"{middleware.__class__.__name__}.modify_request "
                    "must return a RawRequest"
                )

    def apply_response_middlewares(self, response) -> Any:
        for middleware in self._middlewares:
            response = middleware.modify_response(response)
            # If the result of .modify_response() is not a Response,
            # don't care about it. It's not the middlewares fault
            # if the user doesn't know what they're doing.
        return response

    def _execute(self, func, *args, **kwargs):
        kwargs, self_, cls_ = self.merge_args_and_kwargs(func, *args, **kwargs)
        self.update_configuration(self_, cls_)
        self.prepare_request(func, **kwargs)
        self.apply_request_middlewares(func, **kwargs)
        with httpx.Client(follow_redirects=True) as client:
            httpx_request = self.raw_request.to_httpx_request()
            httpx_response = self.wait_for(
                func=client.send, request=httpx_request
            )
            response = self.parse_response(
                func=func,
                httpx_request=httpx_request,
                httpx_response=httpx_response,
            )
            return self.apply_response_middlewares(response)
