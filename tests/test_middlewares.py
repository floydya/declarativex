from typing import List

import pytest

from declarativex import BaseClient, http
from declarativex.exceptions import MisconfiguredException
from .fixtures.middlewares.dummy import (
    SyncDummyMiddleware,
    AsyncDummyMiddleware,
    SyncInvalidDummyMiddleware,
    AsyncInvalidDummyMiddleware,
)


class SyncTestClient(BaseClient):
    middlewares = [SyncDummyMiddleware()]
    base_url = "https://jsonplaceholder.typicode.com"

    @http("GET", "/posts")
    def get_posts(self) -> List[dict]:
        pass


class AsyncTestClient(BaseClient):
    middlewares = [AsyncDummyMiddleware()]
    base_url = "https://jsonplaceholder.typicode.com"

    @http("GET", "/posts")
    async def get_posts(self) -> List[dict]:
        pass


def test_sync_middleware():
    client = SyncTestClient()
    posts = client.get_posts()
    # Without middleware, the userId is not present in
    # the query params and len(posts) == 100 (the default
    # number of posts returned by the API)
    # With the middleware, the userId is present in the query
    # params and len(posts) == 10 (the number of posts returned
    # by the API for userId=1)
    assert len(posts) == 10
    assert all(post["userId"] == 1 for post in posts)


@pytest.mark.asyncio
async def test_async_middleware():
    client = AsyncTestClient()
    posts = await client.get_posts()
    # Without middleware, the userId is not present in
    # the query params and len(posts) == 100 (the default
    # number of posts returned by the API)
    # With the middleware, the userId is present in the query
    # params and len(posts) == 10 (the number of posts returned
    # by the API for userId=2)
    assert len(posts) == 10
    assert all(post["userId"] == 2 for post in posts)


def test_async_middleware_in_sync_function():
    @http(
        "GET",
        "/posts",
        base_url="https://jsonplaceholder.typicode.com",
        middlewares=[AsyncDummyMiddleware()],
    )
    def get_posts() -> List[dict]:
        pass

    with pytest.raises(MisconfiguredException) as exc:
        _ = get_posts()

    assert str(exc.value) == (
        "AsyncMiddleware cannot be used with sync functions, "
        "use Middleware instead."
    )


@pytest.mark.asyncio
async def test_sync_middleware_in_async_function():
    @http(
        "GET",
        "/posts",
        base_url="https://jsonplaceholder.typicode.com",
        middlewares=[SyncDummyMiddleware()],
    )
    async def get_posts() -> List[dict]:
        pass

    with pytest.raises(MisconfiguredException) as exc:
        _ = await get_posts()

    assert str(exc.value) == (
        "Middleware cannot be used with async functions, "
        "use AsyncMiddleware instead."
    )


def test_sync_invalid_middleware():
    @http(
        "GET",
        "/posts",
        base_url="https://jsonplaceholder.typicode.com",
        middlewares=[SyncInvalidDummyMiddleware()],
    )
    def get_posts() -> List[dict]:
        pass

    with pytest.raises(MisconfiguredException) as exc:
        _ = get_posts()

    assert str(exc.value) == (
        "SyncInvalidDummyMiddleware.modify_request "
        "must return a RawRequest"
    )


@pytest.mark.asyncio
async def test_async_invalid_middleware():
    @http(
        "GET",
        "/posts",
        base_url="https://jsonplaceholder.typicode.com",
        middlewares=[AsyncInvalidDummyMiddleware()],
    )
    async def get_posts() -> List[dict]:
        pass

    with pytest.raises(MisconfiguredException) as exc:
        _ = await get_posts()

    assert str(exc.value) == (
        "AsyncInvalidDummyMiddleware.modify_request "
        "must return a RawRequest"
    )
