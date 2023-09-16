import asyncio
import sys
import time

import pytest

from declarativex import rate_limiter, BaseClient, http, RateLimitExceeded


class DummyClient(BaseClient):
    base_url = "https://reqres.in/"

    @http("GET", "/api/users")
    async def get_users(self) -> dict:
        ...

    @http("GET", "/api/users/{user_id}")
    async def get_user(self, user_id: int) -> dict:
        ...


class SyncDummyClient(BaseClient):
    base_url = "https://reqres.in/"

    @http("GET", "/api/users")
    def get_users(self) -> dict:
        ...

    @http("GET", "/api/users/{user_id}")
    def get_user(self, user_id: int) -> dict:
        ...


def create_client(*, client, reject: bool):
    client = rate_limiter(max_calls=1, interval=1, reject=reject)(client)()
    
    assert hasattr(client, "_rate_limiter_bucket")
    assert client._rate_limiter_bucket._max_calls == 1
    assert client._rate_limiter_bucket._interval == 1
    
    assert hasattr(client.get_users, "_rate_limiter_bucket")
    assert client.get_users._rate_limiter_bucket._max_calls == 1
    assert client.get_users._rate_limiter_bucket._interval == 1
    assert client.get_users._rate_limiter_bucket == client._rate_limiter_bucket

    return client


@pytest.mark.asyncio
async def test_rate_limiter():
    client = create_client(client=DummyClient, reject=False)
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


@pytest.mark.asyncio
async def test_rate_limiter_rejection():
    client = create_client(client=DummyClient, reject=True)
    client._rate_limiter_bucket.refill()
    _ = await client.get_users()
    with pytest.raises(RateLimitExceeded):
        await client.get_users()
        await client.get_users()


def test_rate_limiter_sync():
    client = create_client(client=SyncDummyClient, reject=False)
    start = time.perf_counter()
    for i in range(2):
        client.get_users()
        client.get_user(1)
    total = time.perf_counter() - start
    assert 3.0 < total < 3.3

    client._rate_limiter_bucket.refill()

    start = time.perf_counter()
    for i in range(3):
        client.get_users()
    total = time.perf_counter() - start
    assert 2 < total < 2.5


def test_rate_limiter_sync_rejection():
    client = create_client(client=SyncDummyClient, reject=True)
    client._rate_limiter_bucket.refill()
    _ = client.get_users()
    with pytest.raises(RateLimitExceeded):
        client.get_users()
        client.get_users()
