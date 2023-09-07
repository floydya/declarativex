from typing import Dict, Optional


class BaseClient:
    """
    Base class for declarative HTTP clients.

    Parameters:
        base_url: Base URL for the client.
        default_headers: Default headers for the client.
        default_query_params: Default query parameters for the client.
    """

    base_url: str = ""
    default_headers: Dict[str, str] = {}
    default_query_params: Dict[str, str] = {}

    def __init__(
        self,
        base_url: Optional[str] = None,
        default_headers: Optional[Dict[str, str]] = None,
        default_query_params: Optional[Dict[str, str]] = None,
    ) -> None:
        self.base_url = base_url or self.base_url
        if not self.base_url:
            raise ValueError("base_url is required")
        self.default_headers = default_headers or self.default_headers
        self.default_query_params = (
            default_query_params or self.default_query_params
        )


__all__ = ["BaseClient"]
