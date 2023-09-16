import logging
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from declarativex import Middleware, http, MisconfiguredException


class FooMiddleware(Middleware):
    def __call__(self, *, request, call_next):
        logging.info("pre FooMiddleware")
        response = call_next(request)
        logging.info("post FooMiddleware")
        return response


class BarMiddleware(Middleware):
    def __call__(self, *, request, call_next):
        logging.info("pre BarMiddleware")
        response = call_next(request)
        logging.info("post BarMiddleware")
        return response


class AsyncFooMiddleware(Middleware):
    async def __call__(self, *, request, call_next):
        logging.info("pre AsyncFooMiddleware")
        response = await call_next(request)
        logging.info("post AsyncFooMiddleware")
        return response


class AsyncBarMiddleware(Middleware):
    async def __call__(self, *, request, call_next):
        logging.info("pre AsyncBarMiddleware")
        response = await call_next(request)
        logging.info("post AsyncBarMiddleware")
        return response


def test_sync_middleware():
    @http(
        "GET",
        "api/users",
        base_url="https://reqres.in",
        middlewares=[FooMiddleware(), BarMiddleware()],
    )
    def get_users():
        pass

    get_users()


@pytest.mark.asyncio
async def test_async_middleware():
    @http(
        "GET",
        "api/users",
        base_url="https://reqres.in",
        middlewares=[AsyncFooMiddleware(), AsyncBarMiddleware()],
    )
    async def get_users():
        pass

    await get_users()


@pytest.mark.asyncio
async def test_sync_async_middleware():
    @http(
        "GET",
        "api/users",
        base_url="https://reqres.in",
        middlewares=[FooMiddleware(), AsyncBarMiddleware()],
    )
    async def get_users():
        pass

    with pytest.raises(MisconfiguredException) as exc:
        await get_users()

    assert str(exc.value) == (
        "Cannot use sync middleware(FooMiddleware) with async function"
    )


def test_async_sync_middleware():
    @http(
        "GET",
        "api/users",
        base_url="https://reqres.in",
        middlewares=[AsyncFooMiddleware(), BarMiddleware()],
    )
    def get_users():
        pass

    with pytest.raises(MisconfiguredException) as exc:
        get_users()

    assert str(exc.value) == (
        "Cannot use async middleware(AsyncFooMiddleware) with sync function"
    )


def test_middleware_creation_with_wrong_signature():
    with pytest.raises(TypeError) as exc:

        class CustomMiddleware(Middleware):
            def __call__(self, *, request):
                pass

    assert str(exc.value) == (
        "Expected parameter 'call_next' in CustomMiddleware.__call__"
    )

    with pytest.raises(TypeError) as exc:

        class CustomMiddleware(Middleware):
            def __call__(self, *, request, call_next, extra):
                pass

    assert str(exc.value) == (
        "Unexpected parameters ['extra'] in CustomMiddleware.__call__"
    )


def test_middleware_dont_call_client(mocker: MockerFixture):
    class CacheMiddleware(Middleware):
        cache = {}

        def add_to_cache(self, url, response):
            self.cache[url] = response

        def get_from_cache(self, url):
            return self.cache.get(url, None)

        def __call__(self, *, request, call_next):
            if request.method != "GET":
                return call_next(request)
            url = request.url()
            if url in self.cache:
                return self.get_from_cache(url)
            response = call_next(request)
            self.add_to_cache(url, response)
            return response

    middleware = CacheMiddleware()

    add = mocker.patch.object(
        CacheMiddleware,
        "add_to_cache",
        MagicMock(wraps=middleware.add_to_cache),
    )
    get = mocker.patch.object(
        CacheMiddleware,
        "get_from_cache",
        MagicMock(wraps=middleware.get_from_cache),
    )

    @http(
        "GET",
        "api/users",
        base_url="https://reqres.in",
        middlewares=[CacheMiddleware()],
    )
    def get_users():
        pass

    get_users()
    assert get.call_count == 0
    assert add.call_count == 1
    get_users()
    assert get.call_count == 1
    assert add.call_count == 1
    get_users()
    assert get.call_count == 2
    assert add.call_count == 1
