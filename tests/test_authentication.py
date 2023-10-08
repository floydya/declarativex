from typing import List, Coroutine, Callable

import pytest

from declarativex import BaseClient, http, Middleware
from declarativex.auth import (
    BasicAuth,
    BearerAuth,
    HeaderAuth,
    QueryParamsAuth,
)
from declarativex.dependencies import Location
from declarativex.models import RawRequest


class AsyncTestMiddleware(Middleware):
    def __init__(self, accessor: Location, key: str, waiting_for: str):
        self.accessor = accessor.value
        self.key = key
        self.waiting_for = waiting_for

    async def __call__(
        self,
        *,
        request: RawRequest,
        call_next,
    ):
        location = getattr(request, self.accessor)
        assert self.key in location
        assert location[self.key] == self.waiting_for
        return await call_next(request)


class Client(BaseClient):
    base_url = "https://jsonplaceholder.typicode.com/"

    @http(
        "GET",
        "/posts",
        auth=BasicAuth("username", "password"),
        middlewares=[
            AsyncTestMiddleware(
                Location.headers,
                "Authorization",
                "Basic dXNlcm5hbWU6cGFzc3dvcmQ=",
            )
        ],
    )
    async def get_posts(self) -> List[dict]:
        ...

    @http(
        "GET",
        "/posts",
        auth=BearerAuth("token12345"),
        middlewares=[
            AsyncTestMiddleware(
                Location.headers, "Authorization", "Bearer token12345"
            )
        ],
    )
    async def get_posts_with_bearer(self) -> List[dict]:
        ...

    @http(
        "GET",
        "/posts",
        auth=HeaderAuth("X-Auth", "token12345"),
        middlewares=[
            AsyncTestMiddleware(Location.headers, "X-Auth", "token12345")
        ],
    )
    async def get_posts_with_custom_auth(self) -> List[dict]:
        ...

    @http(
        "GET",
        "/posts",
        auth=QueryParamsAuth("api_token", "test12345"),
        middlewares=[
            AsyncTestMiddleware(
                Location.query_params, "api_token", "test12345"
            )
        ],
    )
    async def get_posts_with_key_in_query(self) -> List[dict]:
        ...


client = Client()


@pytest.mark.parametrize(
    'coro',
    [
        client.get_posts,
        client.get_posts_with_bearer,
        client.get_posts_with_custom_auth,
        client.get_posts_with_key_in_query,
    ]
)
@pytest.mark.asyncio
async def test_auth(coro: Callable[..., Coroutine]):
    await coro()
