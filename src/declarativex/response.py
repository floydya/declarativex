import dataclasses
from typing import (
    Awaitable,
    Callable,
    Dict,
    Generic,
    TypeVar,
    Union,
)

import httpx

from .compatibility import parse_obj_as
from .request import Request

R = TypeVar("R")


@dataclasses.dataclass
class Response(Generic[R]):
    status_code: int
    headers: Dict[str, str]
    content_type: str
    data: R
    request: Request


def process_response(
    response: httpx.Response,
    request: Request,
    func: Callable[..., Union[R, Awaitable[R]]],
) -> Response[R]:
    return_type = func.__annotations__.get("return")
    response_data = parse_obj_as(return_type or dict, response.json())
    return Response(
        status_code=response.status_code,
        headers={**response.headers},
        content_type=response.headers.get("content-type"),
        data=response_data,
        request=request,
    )
