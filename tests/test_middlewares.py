import json

import httpx
import pytest

from src.declarativex import (
    BaseClient,
    Middleware,
    AsyncMiddleware,
    declare,
    JsonField,
    Header,
    Cookie,
    Json,
)
from src.declarativex.exceptions import MisconfiguredException


class TestMiddleware(Middleware[dict]):
    def modify_request(self, request: httpx.Request):
        request.url = httpx.URL("https://jsonplaceholder.typicode.com/posts/3")
        return request

    def modify_response(self, response: dict) -> dict:
        return {**response, "title": "test_title"}


class AsyncTestMiddleware(AsyncMiddleware[dict]):
    async def modify_request(self, request: httpx.Request):
        assert "X-Api-Key" in request.headers
        assert request.headers["X-Api-Key"] == "test_key"
        assert "Cookie" in request.headers
        assert request.headers["Cookie"] == "session=test_session"
        return request

    async def modify_response(self, response: dict) -> dict:
        return {**response, "title": "async_test_title"}


class JsonTestClient(BaseClient):
    base_url = "https://jsonplaceholder.typicode.com"
    middlewares = [TestMiddleware()]

    @declare("GET", "/posts/{post_id}")
    def get_post(self, post_id: int) -> dict:
        pass  # pragma: no cover

    @declare("POST", "/posts", middlewares=[AsyncTestMiddleware()])
    def create_post(self, title: str = JsonField()) -> dict:
        pass  # pragma: no cover


class AsyncJsonTestClient(BaseClient):
    base_url = "https://jsonplaceholder.typicode.com"
    middlewares = [AsyncTestMiddleware()]

    @declare("POST", "/posts")
    async def create_post(
        self,
        post: str = Json(...),
        x_api_key: str = Header("X-Api-Key"),
        session: str = Cookie("session"),
    ) -> dict:
        pass  # pragma: no cover

    @declare("PATCH", "/posts", middlewares=[TestMiddleware()])
    async def update_post(self, title: str = JsonField()) -> dict:
        pass  # pragma: no cover


class TestClient:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = JsonTestClient()

    def test_middleware(self):
        post = self.client.get_post(1)
        assert post["id"] == 3
        assert post["title"] == "test_title"

    def test_async_middleware_with_sync_method(self):
        with pytest.raises(MisconfiguredException) as err:
            self.client.create_post(title="test")

        assert str(err.value) == (
            "AsyncMiddleware cannot be used with sync functions, "
            "use Middleware instead."
        )


class TestAsyncClient:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = AsyncJsonTestClient()

    @pytest.mark.asyncio
    async def test_async_middleware(self):
        post = json.dumps({"title": "test"})

        post = await self.client.create_post(
            post=post, x_api_key="test_key", session="test_session"
        )
        assert post["id"] == 101
        assert post["title"] == "async_test_title"

    @pytest.mark.asyncio
    async def test_middleware_with_async_method(self):
        with pytest.raises(MisconfiguredException) as err:
            await self.client.update_post(title="test")

        assert str(err.value) == (
            "Middleware cannot be used with async functions, "
            "use AsyncMiddleware instead."
        )
