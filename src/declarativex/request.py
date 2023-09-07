import dataclasses
from typing import Any, Callable, Dict, Optional
from urllib.parse import urlencode

from .dependencies import BodyField, Json, Path, Query
from .helpers import get_params


@dataclasses.dataclass
class Request:
    method: str
    url: str
    query: str
    data: Optional[Dict[str, Any]]
    headers: Dict[str, str]
    content_type: str

    @classmethod
    def build_request(
        cls,
        func: Callable[..., Any],
        method: str,
        path: str,
        base_url: str,
        default_query_params: Optional[Dict[str, Any]] = None,
        default_headers: Optional[Dict[str, str]] = None,
        **values,
    ) -> "Request":
        query: Dict[str, Any] = default_query_params or {}

        url = f"{base_url}{path}"
        path_params = {}

        body = {}
        data = {}

        for options in get_params(func, path, **values):
            if isinstance(options.location, Path):
                path_params[options.name] = Path.parse(options.value)
            elif isinstance(options.location, Query):
                query[options.name] = Query.parse(options.value)
            elif isinstance(options.location, BodyField):
                if method == "GET":
                    raise ValueError(
                        "BodyField field is not supported for GET requests"
                    )
                body[options.name] = BodyField.parse(options.value)
            elif isinstance(options.location, Json):
                if method == "GET":
                    raise ValueError(
                        "Json field is not supported for GET requests"
                    )
                data = Json.parse(options.value)

        url = url.format(**path_params)
        query_params = urlencode(query, doseq=True)
        return cls(
            method=method,
            url=f"{url}?{query_params}" if query_params else url,
            query=query_params,
            data=data.update(body),
            headers=default_headers or {},
            content_type="application/json",
        )
