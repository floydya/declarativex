import asyncio
from functools import partial, wraps
from typing import Any, Callable, Optional, TYPE_CHECKING
from urllib.parse import urlencode

import httpx

if TYPE_CHECKING:
    from .client import BaseClient  # pragma: no cover


def http_method(
    method: str, path: str, timeout: Optional[int] = None
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(
            cls_instance: "BaseClient", *args: Any, **kwargs: Any
        ) -> Any:
            params, url, data, headers = cls_instance.prepare_request(
                func, **kwargs
            )
            if params:
                url = f"{url}?{urlencode(params)}"
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.request(
                        method,
                        url,
                        headers=headers,
                        json=data,
                        timeout=timeout,
                    )
            except httpx.ReadTimeout:
                raise TimeoutError(
                    f"Request timed out after {timeout} seconds"
                )
            return cls_instance.process_response(response, func)

        @wraps(func)
        def sync_wrapper(
            cls_instance: "BaseClient", *args: Any, **kwargs: Any
        ) -> Any:
            params, url, data, headers = cls_instance.prepare_request(
                func, **kwargs
            )
            if params:
                url = f"{url}?{urlencode(params)}"
            try:
                with httpx.Client() as client:
                    response = client.request(
                        method,
                        url,
                        headers=headers,
                        json=data,
                        timeout=timeout,
                    )
            except httpx.ReadTimeout:
                raise TimeoutError(
                    f"Request timed out after {timeout} seconds"
                )
            return cls_instance.process_response(response, func)

        setattr(func, "_http_method", method)
        setattr(func, "_path", path)

        return (
            async_wrapper
            if asyncio.iscoroutinefunction(func)
            else sync_wrapper
        )

    return decorator


# HTTP Methods Decorators
get = partial(http_method, "GET")
post = partial(http_method, "POST")
patch = partial(http_method, "PATCH")
put = partial(http_method, "PUT")
delete = partial(http_method, "DELETE")


__all__ = ["get", "post", "patch", "put", "delete"]
