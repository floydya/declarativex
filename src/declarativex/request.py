from typing import Any, Callable, Dict, Optional, TypedDict, cast

import httpx

from .dependencies import (
    JsonField,
    Json,
    Path,
    Query,
    Header,
    Cookie,
)
from .helpers import get_params


class RequestDict(TypedDict):
    method: str
    url: httpx.URL
    params: Optional[Dict[str, Any]]
    headers: httpx.Headers
    cookies: Optional[httpx.Cookies]
    json: Optional[Dict[str, Any]]
    data: Optional[Dict[str, Any]]
    timeout: Optional[float]


def build_request(
    func: Callable[..., Any],
    method: str,
    path: str,
    base_url: str,
    timeout: Optional[float] = None,
    default_query_params: Optional[Dict[str, Any]] = None,
    default_headers: Optional[Dict[str, str]] = None,
    **values,
) -> RequestDict:
    url: str = f"{base_url}{path}"
    params: Dict[str, Any] = default_query_params or {}
    _headers: Dict[str, Any] = default_headers or {}
    path_params: Dict[str, str] = {}
    json_fields: Dict[str, Any] = {}
    json: Optional[Dict[str, Any]] = None
    _cookies: Dict[str, Any] = {}
    form_data: Optional[Dict[str, Any]] = None

    for dependency in get_params(func, path, **values):
        if isinstance(dependency, Path):
            path_params[dependency.field_name] = cast(str, dependency.value)
        elif isinstance(dependency, Json):
            json = cast(dict, dependency.value)
        elif dependency.value is not None:
            value = cast(str, dependency.value)
            if isinstance(dependency, JsonField):
                json_fields[dependency.field_name] = value
            elif isinstance(dependency, Header):
                _headers[dependency.field_name] = value
            elif isinstance(dependency, Cookie):
                _cookies[dependency.field_name] = value
            elif isinstance(dependency, Query):
                params[dependency.field_name] = value

    if json and json_fields:
        json = json.update(json_fields)

    headers = httpx.Headers(headers=_headers)
    if "content-type" not in headers:
        headers.update({"Content-Type": "application/json"})

    cookies = httpx.Cookies(cookies=_cookies) if _cookies else None

    return RequestDict(
        method=method,
        url=httpx.URL(url.format(**path_params)),
        params=params or None,
        headers=headers,
        cookies=cookies or None,
        json=json,
        data=form_data or None,
        timeout=timeout,
    )
