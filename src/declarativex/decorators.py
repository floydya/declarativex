import asyncio
from functools import wraps
from typing import Any, Callable, Optional, TYPE_CHECKING
from urllib.parse import urlencode

import httpx

if TYPE_CHECKING:
    from .client import BaseClient  # pragma: no cover


def http_method_decorator(
    method: str, path: str, timeout: Optional[int] = None
) -> Callable[[Callable], Callable]:
    """
    Decorator to define an HTTP method on a client class.
    :param method: HTTP method to define, always uppercase.
    :param path: Path to use for the HTTP request.
    :param timeout: Timeout for the HTTP request.
    :return: Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        """
        Decorator function.
        :param func: Function to decorate.
        :return: Decorated function.
        """
        @wraps(func)
        async def async_wrapper(
            cls_instance: "BaseClient", *args: Any, **kwargs: Any
        ) -> Any:
            """
            Wrapper for async functions.
            :param cls_instance: Instance of the client class.
            :param args: Positional arguments of client method.
            :param kwargs: Keyword arguments of client method.
            :return: Response of the async HTTP request.
            """
            params, url, data, headers = cls_instance.prepare_request(
                func, **kwargs
            )
            if params:
                # If there are query parameters, add them to the URL.
                url = f"{url}?{urlencode(params)}"
            try:
                # Make the HTTP request.
                async with httpx.AsyncClient() as client:
                    response = await client.request(
                        method,
                        url,
                        headers=headers,
                        json=data,
                        timeout=timeout,
                    )
            except httpx.ReadTimeout:
                # If the request times out, raise a built-in TimeoutError.
                # This is done to make the error message more user-friendly.
                # You don't need to import httpx to catch the error.
                raise TimeoutError(
                    f"Request timed out after {timeout} seconds"
                )
            return cls_instance.process_response(response, func)

        @wraps(func)
        def sync_wrapper(
            cls_instance: "BaseClient", *args: Any, **kwargs: Any
        ) -> Any:
            """
            Wrapper for sync functions.
            :param cls_instance: Instance of the client class.
            :param args: Positional arguments of client method.
            :param kwargs: Keyword arguments of client method.
            :return: Response of the sync HTTP request.
            """
            params, url, data, headers = cls_instance.prepare_request(
                func, **kwargs
            )
            if params:
                # If there are query parameters, add them to the URL.
                url = f"{url}?{urlencode(params)}"
            try:
                # Make the HTTP request.
                with httpx.Client() as client:
                    response = client.request(
                        method,
                        url,
                        headers=headers,
                        json=data,
                        timeout=timeout,
                    )
            except httpx.ReadTimeout:
                # If the request times out, raise a built-in TimeoutError.
                # This is done to make the error message more user-friendly.
                # You don't need to import httpx to catch the error.
                raise TimeoutError(
                    f"Request timed out after {timeout} seconds"
                )
            return cls_instance.process_response(response, func)

        # Set attributes on the function to allow the client class to
        # introspect them.
        setattr(func, "_http_method", method)
        setattr(func, "_path", path)

        return (
            async_wrapper
            if asyncio.iscoroutinefunction(func)
            else sync_wrapper
        )

    return decorator


# Explicitly defined decorators for each HTTP method to allow IDEs to
# provide autocompletion for the path and timeout parameters.

def get(
    path: str, timeout: Optional[int] = None
) -> Callable[[Callable], Callable]:
    """
    Decorator to define a GET method on a client class.
    :param path: Path to use for the HTTP request.
    :param timeout: Timeout for the HTTP request.
    :return: Decorator function.
    """
    return http_method_decorator("GET", path, timeout)


def post(
    path: str, timeout: Optional[int] = None
) -> Callable[[Callable], Callable]:
    """
    Decorator to define a POST method on a client class.
    :param path: Path to use for the HTTP request.
    :param timeout: Timeout for the HTTP request.
    :return: Decorator function.
    """
    return http_method_decorator("POST", path, timeout)


def patch(
    path: str, timeout: Optional[int] = None
) -> Callable[[Callable], Callable]:
    """
    Decorator to define a PATCH method on a client class.
    :param path: Path to use for the HTTP request.
    :param timeout: Timeout for the HTTP request.
    :return: Decorator function.
    """
    return http_method_decorator("PATCH", path, timeout)


def put(
    path: str, timeout: Optional[int] = None
) -> Callable[[Callable], Callable]:
    """
    Decorator to define a PUT method on a client class.
    :param path: Path to use for the HTTP request.
    :param timeout: Timeout for the HTTP request.
    :return: Decorator function.
    """
    return http_method_decorator("PUT", path, timeout)


def delete(
    path: str, timeout: Optional[int] = None
) -> Callable[[Callable], Callable]:
    """
    Decorator to define a DELETE method on a client class.
    :param path: Path to use for the HTTP request.
    :param timeout: Timeout for the HTTP request.
    :return: Decorator function.
    """
    return http_method_decorator("DELETE", path, timeout)


__all__ = ["get", "post", "patch", "put", "delete"]
