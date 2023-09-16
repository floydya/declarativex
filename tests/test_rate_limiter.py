import asyncio
import sys
import time

import pytest

from declarativex import rate_limiter, BaseClient, http


@rate_limiter(max_calls=1, interval=1)
class DummyClient(BaseClient):
    base_url = "https://reqres.in/"

    @http("GET", "/api/users")
    async def get_users(self) -> dict:
        ...

    @http("GET", "/api/users/{user_id}")
    async def get_user(self, user_id: int) -> dict:
        ...


@pytest.mark.asyncio
async def test_rate_limiter():
    client = DummyClient()

    assert hasattr(client, "_rate_limiter_bucket")
    assert client._rate_limiter_bucket._max_calls == 1
    assert client._rate_limiter_bucket._interval == 1

    assert hasattr(client.get_users, "_rate_limiter_bucket")
    assert client.get_users._rate_limiter_bucket._max_calls == 1
    assert client.get_users._rate_limiter_bucket._interval == 1
    assert client.get_users._rate_limiter_bucket == client._rate_limiter_bucket

    start = time.perf_counter()
    for i in range(2):
        await client.get_users()
        await client.get_user(1)
    total = time.perf_counter() - start
    assert 3.0 < total < 3.3

    client._rate_limiter_bucket.refill()

    if sys.version_info >= (3, 10):
        start = time.perf_counter()
        asyncio.get_event_loop()
        await asyncio.gather(*[client.get_users() for _ in range(3)])
        total = time.perf_counter() - start
        assert 2 < total < 2.5
