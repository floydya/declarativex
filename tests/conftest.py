import typing
from unittest.mock import patch

import httpx
import pytest
from starlette.testclient import (
    TestClient,
    _AsyncBackend,
    _is_asgi3,
    ASGI3App,
    _TestClientTransport,
)

from tests.app.main import app as mock_app


class AsyncClient(httpx.AsyncClient):
    def __init__(self, *args, **kwargs):  # pragma: no cover
        kwargs["app"] = mock_app
        kwargs["base_url"] = "http://testserver"
        super().__init__(*args, **kwargs)


class Client(TestClient):
    def __init__(
        self,
        base_url: str = "http://testserver",
        raise_server_exceptions: bool = True,
        root_path: str = "",
        backend: str = "asyncio",
        backend_options: typing.Optional[typing.Dict[str, typing.Any]] = None,
        cookies: httpx._client.CookieTypes = None,
        headers: typing.Dict[str, str] = None,
        follow_redirects: bool = True,
        timeout: typing.Optional[float] = None,
    ) -> None:
        app = mock_app
        self.async_backend = _AsyncBackend(
            backend=backend, backend_options=backend_options or {}
        )
        if _is_asgi3(app):
            app = typing.cast(ASGI3App, app)
            asgi_app = app
        else:
            app = typing.cast(ASGI2App, app)  # type: ignore[assignment]
            asgi_app = _WrapASGI2(app)  # type: ignore[arg-type]
        self.app = asgi_app
        self.app_state: typing.Dict[str, typing.Any] = {}
        transport = _TestClientTransport(
            self.app,
            portal_factory=self._portal_factory,
            raise_server_exceptions=raise_server_exceptions,
            root_path=root_path,
            app_state=self.app_state,
        )
        if headers is None:
            headers = {}
        headers.setdefault("user-agent", "testclient")
        super(TestClient, self).__init__(
            app=self.app,
            base_url=base_url,
            headers=headers,
            transport=transport,
            follow_redirects=follow_redirects,
            cookies=cookies,
            timeout=timeout,
        )


@pytest.fixture(scope="class")
def mock_client():  # pragma: no cover
    with patch("src.declarativex.methods.httpx.Client", Client):
        yield


@pytest.fixture(scope="class")
def mock_async_client():  # pragma: no cover
    with patch("src.declarativex.methods.httpx.AsyncClient", AsyncClient):
        yield
