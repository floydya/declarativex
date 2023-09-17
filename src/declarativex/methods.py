import asyncio
import inspect
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


def http(
    method: str,
    path: str,
    *,
    timeout: Optional[float] = None,
    base_url: str = "",
    default_query_params: Optional[Dict[str, Any]] = None,
    default_headers: Optional[Dict[str, str]] = None,
    middlewares: Optional[Sequence[Middleware]] = None,
    error_mappings: Optional[Dict[int, Type]] = None,
) -> Callable[..., ReturnType]:
    client_configuration = ClientConfiguration.create(
        base_url=base_url,
        default_query_params=default_query_params,
        default_headers=default_headers,
        middlewares=middlewares,
        error_mappings=error_mappings,
    )

    endpoint_configuration = EndpointConfiguration(
        method=method,
        path=path,
        timeout=timeout,
        client_configuration=client_configuration,
    )

    def wrapper(func):
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def inner(*args: Any, **kwargs: Any):
                return await AsyncExecutor(
                    endpoint_configuration=endpoint_configuration
                ).execute(func, *args, **kwargs)

        else:

            @wraps(func)
            def inner(*args: Any, **kwargs: Any):
                return SyncExecutor(
                    endpoint_configuration=endpoint_configuration
                ).execute(func, *args, **kwargs)

        setattr(inner, DECLARED_MARK, True)
        inner.__annotations__["return"] = (
            inspect.signature(func).return_annotation
        )
        return inner

    return wrapper
