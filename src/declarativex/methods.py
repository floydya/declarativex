# pylint: disable=no-member
import inspect
import logging
from functools import wraps
from typing import (
    Any,
    Callable,
    Dict,
    Optional,
    Type,
    Sequence,
)

from .executors import AsyncExecutor, SyncExecutor
from .middlewares import Middleware
from .models import ClientConfiguration, EndpointConfiguration
from .utils import ReturnType, DECLARED_MARK


class http:
    def __init__(
        self,
        method: str,
        path: str,
        *,
        timeout: Optional[float] = None,
        base_url: str = "",
        default_query_params: Optional[Dict[str, Any]] = None,
        default_headers: Optional[Dict[str, str]] = None,
        middlewares: Optional[Sequence[Middleware]] = None,
        error_mappings: Optional[Dict[int, Type]] = None,
    ):
        self._client_configuration = ClientConfiguration.create(
            base_url=base_url,
            default_query_params=default_query_params,
            default_headers=default_headers,
            middlewares=middlewares,
            error_mappings=error_mappings,
        )
        self._endpoint_configuration = EndpointConfiguration(
            method=method,
            path=path,
            timeout=timeout,
            client_configuration=self._client_configuration,
        )

    def __call__(
        self, func: Callable[..., ReturnType]
    ) -> Callable[..., ReturnType]:
        @wraps(func)
        def inner(*args, **kwargs):
            frame = inspect.currentframe().f_back
            if (
                frame.f_code.co_flags & inspect.CO_COROUTINE
            ):
                return AsyncExecutor(
                    endpoint_configuration=self._endpoint_configuration
                ).execute(func, *args, **kwargs)
            logging.error(f"__call__, {func}, {args}, {kwargs}")
            return SyncExecutor(
                endpoint_configuration=self._endpoint_configuration
            ).execute(func, *args, **kwargs)

        setattr(inner, DECLARED_MARK, True)
        return_type = inspect.signature(func).return_annotation
        inner.__annotations__["return"] = return_type
        return inner
