import asyncio
import time
from unittest.mock import patch, MagicMock

import pytest

from declarativex import rate_limiter
from src.declarativex import BaseClient, declare


class MyTestClient(BaseClient):
    base_url = "https://test.com"

    @rate_limiter(max_calls=1, interval=1)
    @declare("GET", "/posts/{id}")
    async def async_get_post(self, id: int) -> dict:
        pass

    @rate_limiter(max_calls=1, interval=1)
    @declare("GET", "/posts/{id}")
    def sync_get_post(self, id: int) -> dict:
        pass


class TestRateLimit:
    @pytest.fixture(autouse=True)
    def setup(self, mock_async_client, mock_client):
        self.client = MyTestClient()

    @pytest.mark.asyncio
    async def test_async_rate_limit(self, mock_async_client):
        with patch(
            "src.declarativex.rate_limiter.asyncio.sleep",
            MagicMock(wraps=asyncio.sleep),
        ):
            current_time = time.perf_counter()
            for i in range(3):
                result = await self.client.async_get_post(i)
                assert "id" in result
            total_time = time.perf_counter() - current_time
            assert 2 < total_time < 3

    def test_sync_rate_limit(self, mock_client):
        with patch(
            "src.declarativex.rate_limiter.time.sleep",
            MagicMock(wraps=time.sleep),
        ):
            current_time = time.perf_counter()
            for i in range(3):
                result = self.client.sync_get_post(i)
                assert "id" in result
            total_time = time.perf_counter() - current_time
            assert 2 < total_time < 3
