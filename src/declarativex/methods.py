import asyncio
import inspect
from functools import wraps
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Generic,
    Optional,
    Protocol,
    Tuple,
    TypeVar,
    Union,
)
from httpx import AsyncClient, Client, ReadTimeout

from . import BaseClient
from .request import Request
from .response import Response, process_response

ReturnType = TypeVar("ReturnType")
SUPPORTED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}


class BaseClientProtocol(Protocol):
    base_url: str
    default_query_params: Optional[Dict[str, Any]]
    headers: Optional[Dict[str, str]]


class RequestExecutor(Generic[ReturnType]):
    method: str
    path: str
    timeout: Optional[int]
    base_url: str
    default_query_params: Dict[str, Any]
    default_headers: Dict[str, str]

    def __init__(
        self,
        method: str,
        path: str,
        timeout: Optional[int] = None,
        base_url: str = "",
        default_query_params: Optional[Dict[str, Any]] = None,
        default_headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self.method = method
        self.path = path
        self.timeout = timeout
        self.base_url = base_url
        self.default_query_params = default_query_params or {}
        self.default_headers = default_headers or {}

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

    def build_request(
        self, func: Callable[..., ReturnType], *args, **kwargs
    ) -> Request:
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
        return Request.build_request(
            func=func,
            method=self.method,
            path=self.path,
            base_url=base_url,
            default_query_params=query_params,
            default_headers=headers,
            **kwargs,
        )

    async def execute_async(
        self,
        func: Callable[..., ReturnType],
        *args: Any,
        **kwargs: Any,
    ) -> Response[ReturnType]:
        request = self.build_request(func, *args, **kwargs)

        try:
            async with AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    request.method,
                    request.url,
                    headers=request.headers,
                    json=request.data,
                )
        except ReadTimeout:
            raise TimeoutError(
                f"Request timed out after {self.timeout} seconds"
            )

        return process_response(response, request, func)

    def execute_sync(
        self,
        func: Callable[..., ReturnType],
        *args: Any,
        **kwargs: Any,
    ) -> Response[ReturnType]:
        request = self.build_request(func, *args, **kwargs)
        try:
            with Client(timeout=self.timeout) as client:
                response = client.request(
                    request.method,
                    request.url,
                    headers=request.headers,
                    json=request.data,
                )
        except ReadTimeout:
            raise TimeoutError(
                f"Request timed out after {self.timeout} seconds"
            )

        return process_response(response, request, func)


def declare(
    method: str,
    path: str,
    timeout: Optional[int] = None,
    base_url: str = "",
    default_query_params: Optional[Dict[str, Any]] = None,
    default_headers: Optional[Dict[str, str]] = None,
):
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
    )

    def wrapper(func: Callable[..., Union[ReturnType, Awaitable[ReturnType]]]):
        @wraps(func)
        def inner(
            *args: Any, **kwargs: Any
        ) -> Union[Response[ReturnType], Awaitable[Response[ReturnType]]]:
            if asyncio.iscoroutinefunction(func):
                return executor.execute_async(func, *args, **kwargs)
            return executor.execute_sync(func, *args, **kwargs)

        return inner

    return wrapper
