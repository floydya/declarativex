import asyncio
import inspect
import warnings
from functools import wraps
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_type_hints,
    cast,
    Sequence,
)

import httpx
from httpx import AsyncClient, Client

from .client import BaseClient
from .compatibility import parse_obj_as
from .dependencies import JsonField, Json
from .exceptions import MisconfiguredException, TimeoutException
from .middlewares import Middleware, AsyncMiddleware
from .request import build_request, RequestDict

ReturnType = TypeVar("ReturnType")
SUPPORTED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}


class RequestExecutor:
    method: str
    path: str
    timeout: Optional[int]
    base_url: str
    default_query_params: Dict[str, Any]
    default_headers: Dict[str, str]
    middlewares: Sequence[Union[Middleware, AsyncMiddleware]]

    def __init__(
        self,
        method: str,
        path: str,
        timeout: Optional[int] = None,
        base_url: str = "",
        default_query_params: Optional[Dict[str, Any]] = None,
        default_headers: Optional[Dict[str, str]] = None,
        middlewares: Optional[
            Sequence[Union[Middleware, AsyncMiddleware]]
        ] = None,
    ) -> None:
        self.method = method
        self.path = path
        self.timeout = timeout
        self.base_url = base_url
        self.default_query_params = default_query_params or {}
        self.default_headers = default_headers or {}
        self.middlewares = middlewares or []

    @staticmethod
    def update_kwargs_with_args(
        func, *args, **kwargs
    ) -> Tuple[Union[BaseClient, None], Dict[str, Any]]:
        cls_instance = None
        signature = inspect.signature(func)
        param_names = list(signature.parameters.keys())
        kwargs.update(dict(zip(param_names, args)))
        self_, cls_ = kwargs.pop("self", None), kwargs.pop("cls", None)
        if self_ or cls_:
            cls_instance = self_ or cls_
        return cls_instance, kwargs

    def build_request(self, func, *args, **kwargs) -> RequestDict:
        cls_instance, kwargs = self.update_kwargs_with_args(
            func, *args, **kwargs
        )

        cls_base_url = cls_instance.base_url if cls_instance else ""
        cls_query_params = (
            cls_instance.default_query_params if cls_instance else {}
        )
        cls_headers = cls_instance.default_headers if cls_instance else {}
        base_url = cls_base_url or self.base_url
        query_params = {**cls_query_params, **self.default_query_params}
        headers = {**cls_headers, **self.default_headers}
        self.middlewares = (
            [*cls_instance.middlewares, *self.middlewares]
            if cls_instance
            else self.middlewares
        )
        for middleware in self.middlewares:
            middleware.set_func(func)
        return build_request(
            func=func,
            method=self.method,
            path=self.path,
            timeout=self.timeout,
            base_url=base_url,
            default_query_params=query_params,
            default_headers=headers,
            **kwargs,
        )

    @staticmethod
    def _is_list_of_objects(return_type: Type) -> bool:
        if (
            hasattr(return_type, "_name")
            and return_type._name == "List"  # pylint: disable=protected-access
        ):
            return True
        return False

    @classmethod
    def process_response(
        cls, func: Callable[..., ReturnType], response: httpx.Response
    ) -> ReturnType:
        raw_response = response.json()
        return_type: type = cast(type, get_type_hints(func).get("return"))
        return_type = (
            Dict if return_type == type(None) else return_type  # noqa
        )
        is_list = cls._is_list_of_objects(return_type)
        if isinstance(raw_response, list) and not is_list:
            return_type = List[return_type]  # type: ignore[valid-type]
            warnings.warn(
                "Provide a correct return type for "
                "your method, response is a list"
            )
        return parse_obj_as(return_type, raw_response)

    async def execute_async(
        self,
        func,
        *args: Any,
        **kwargs: Any,
    ):
        request_data = self.build_request(func, *args, **kwargs)
        try:
            async with AsyncClient(
                timeout=self.timeout, follow_redirects=True
            ) as client:
                request = client.build_request(**request_data)
                for middleware in self.middlewares:
                    request = await middleware.modify_request(request)  # type: ignore[misc] # noqa
                response = await client.send(request)
        except httpx.TimeoutException:
            raise TimeoutException(
                timeout=self.timeout,
                request=request,
            )
        processed_response = self.process_response(
            func=func, response=response
        )
        for middleware in self.middlewares:
            processed_response = await middleware.modify_response(
                processed_response
            )
        return processed_response

    def execute_sync(
        self,
        func,
        *args: Any,
        **kwargs: Any,
    ):
        request_data = self.build_request(func, *args, **kwargs)
        try:
            with Client(follow_redirects=True) as client:
                request = client.build_request(**request_data)
                for middleware in self.middlewares:
                    request = middleware.modify_request(request)  # type: ignore[assignment] # noqa
                response = client.send(request)
        except httpx.TimeoutException:
            raise TimeoutException(
                timeout=self.timeout,
                request=request,
            )
        processed_response = self.process_response(
            func=func, response=response
        )
        for middleware in self.middlewares:
            processed_response = middleware.modify_response(processed_response)
        return processed_response


def declare(
    method: str,
    path: str,
    *,
    timeout: Optional[int] = None,
    base_url: str = "",
    default_query_params: Optional[Dict[str, Any]] = None,
    default_headers: Optional[Dict[str, str]] = None,
    middlewares: Optional[Sequence[Union[Middleware, AsyncMiddleware]]] = None,
) -> Callable[..., ReturnType]:
    method = method.upper()
    if method not in SUPPORTED_METHODS:
        raise ValueError(
            f"Unsupported method: {method}. "
            f"Supported methods: {SUPPORTED_METHODS}"
        )

    executor: RequestExecutor = RequestExecutor(
        method=method,
        path=path,
        timeout=timeout,
        base_url=base_url,
        default_query_params=default_query_params,
        default_headers=default_headers,
        middlewares=middlewares,
    )

    def wrapper(func):
        signature = inspect.signature(func)
        any_body_or_json_field = any(
            param.default
            for param in signature.parameters.values()
            if isinstance(param.default, (JsonField, Json))
        )
        if method == "GET" and any_body_or_json_field:
            raise MisconfiguredException(
                "BodyField and Json fields are not supported for GET requests"
            )

        func_return_type = get_type_hints(func).get("return")
        if isinstance(func_return_type, type(None)):
            warnings.warn(
                "You must specify return type for your method. "
                f"Example: def {func.__name__}(...) -> dict: ..."
            )

        func.__annotations__["return"] = func_return_type

        @wraps(func)
        def inner(*args: Any, **kwargs: Any):
            if asyncio.iscoroutinefunction(func):
                return executor.execute_async(func, *args, **kwargs)
            return executor.execute_sync(func, *args, **kwargs)

        inner.__annotations__["return"] = func_return_type
        return inner

    return wrapper
