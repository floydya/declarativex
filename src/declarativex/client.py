from typing import Dict, Optional, Union, Sequence, Type

from .exceptions import MisconfiguredException
from .middlewares import Middleware, AsyncMiddleware


class BaseClient:
    """
    Base class for declarative HTTP clients.

    Parameters:
        base_url: Base URL for the client.
        default_headers: Default headers for the client.
        default_query_params: Default query parameters for the client.
        middlewares: List of middlewares for the client.
        error_mappings: Mapping of status codes to exceptions.
    """

    base_url: str = ""
    default_headers: Dict[str, str] = {}
    default_query_params: Dict[str, str] = {}
    middlewares: Sequence[Union[Middleware, AsyncMiddleware]] = []
    error_mappings: Dict[int, Type] = {}

    def __init__(
        self,
        base_url: Optional[str] = None,
        default_headers: Optional[Dict[str, str]] = None,
        default_query_params: Optional[Dict[str, str]] = None,
        middlewares: Optional[
            Sequence[Union[Middleware, AsyncMiddleware]]
        ] = None,
        error_mappings: Optional[Dict[int, Type]] = None,
    ) -> None:
        self.base_url = base_url or self.base_url
        if not self.base_url:
            raise MisconfiguredException("base_url is required")
        self.default_headers = default_headers or self.default_headers
        self.default_query_params = (
            default_query_params or self.default_query_params
        )
        self.middlewares = middlewares or self.middlewares
        self.error_mappings = error_mappings or self.error_mappings


__all__ = ["BaseClient"]
