import asyncio
import sys
import time

import pytest

from declarativex import (
    rate_limiter,
    BaseClient,
    http,
    RateLimitExceeded,
    MisconfiguredException,
)
from declarativex.warnings import DeclarativeWarning


@rate_limiter(max_calls=1, interval=1, reject=False)
class DummyClient(BaseClient):
    base_url = "https://reqres.in/"

    @http("GET", "/api/users")
    async def get_users(self) -> dict:
        ...

    @http("GET", "/api/users/{user_id}")
    async def get_user(self, user_id: int) -> dict:
        ...


@rate_limiter(max_calls=1, interval=1, reject=False)
class SyncDummyClient(BaseClient):
    base_url = "https://reqres.in/"

    @http("GET", "/api/users")
    def get_users(self) -> dict:
        ...

    @http("GET", "/api/users/{user_id}")
    def get_user(self, user_id: int) -> dict:
        ...


@rate_limiter(max_calls=0, interval=1, reject=True)
class RejectDummyClient(BaseClient):
    base_url = "https://reqres.in/"

    @http("GET", "/api/users")
    async def get_users(self) -> dict:
        ...

    @http("GET", "/api/users/{user_id}")
    async def get_user(self, user_id: int) -> dict:
        ...


@rate_limiter(max_calls=0, interval=1, reject=True)
class RejectSyncDummyClient(BaseClient):
    base_url = "https://reqres.in/"

    @http("GET", "/api/users")
    def get_users(self) -> dict:
        ...

    @http("GET", "/api/users/{user_id}")
    def get_user(self, user_id: int) -> dict:
        ...


@pytest.mark.asyncio
async def test_rate_limiter():
    client = DummyClient()
    start = time.perf_counter()
    for i in range(2):
        await client.get_users()
        await client.get_user(1)
    total = time.perf_counter() - start
    assert 3 < total < 4

    client.refill()

    if sys.version_info >= (3, 10):
        start = time.perf_counter()
        asyncio.get_event_loop()
        await asyncio.gather(*[client.get_users() for _ in range(3)])
        total = time.perf_counter() - start
        assert 2 < total < 3


@pytest.mark.asyncio
async def test_rate_limiter_rejection():
    client = RejectDummyClient()
    client.refill()
    with pytest.raises(RateLimitExceeded):
        await client.get_users()


def test_rate_limiter_sync():
    client = SyncDummyClient()
    start = time.perf_counter()
    for i in range(2):
        client.get_users()
        client.get_user(1)
    total = time.perf_counter() - start
    assert 3.0 < total < 3.5

    client.refill()

    start = time.perf_counter()
    for i in range(3):
        client.get_users()
    total = time.perf_counter() - start
    assert 2 < total < 2.5


def test_rate_limiter_sync_rejection():
    client = RejectSyncDummyClient()
    client.refill()
    with pytest.raises(RateLimitExceeded):
        client.get_users()


def test_double_decoration():
    with pytest.raises(MisconfiguredException) as exc:

        @rate_limiter(max_calls=1, interval=1, reject=False)
        class FooClient(BaseClient):
            @rate_limiter(max_calls=1, interval=1, reject=False)
            @http("GET", "/api/users")
            async def get_users(self) -> dict:
                ...

    assert (
        str(exc.value) == "Cannot decorate function with @rate_limiter twice"
    )


def test_unsupported_func_decorated():
    with pytest.warns(DeclarativeWarning) as record:

        @rate_limiter(max_calls=1, interval=1, reject=False)
        def func():
            ...

    assert str(record[0].message) == (
        "rate_limiter decorator is ignored because "
        "not applied to endpoint declaration."
    )
