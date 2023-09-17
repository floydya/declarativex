import asyncio
import time
import warnings
from typing import Annotated
from unittest.mock import MagicMock

import httpx
import pytest
from pytest_mock import MockerFixture

from declarativex import BaseClient, http, retry, TimeoutException, Query


@retry(max_retries=3, delay=0.1, exceptions=(TimeoutException,))
class DummyClient(BaseClient):
    base_url = "https://reqres.in/"

    @http("GET", "/api/users", timeout=0.1)
    async def get_users(self, delay: Annotated[int, Query] = 5) -> dict:
        ...


@retry(max_retries=3, delay=0.1, exceptions=(TimeoutException,))
class SyncDummyClient(BaseClient):
    base_url = "https://reqres.in/"

    @http("GET", "/api/users", timeout=0.1)
    def get_users(self, delay: Annotated[int, Query] = 5) -> dict:
        ...


client = DummyClient()
sync_client = SyncDummyClient()


@pytest.mark.asyncio
async def test_retry(mocker: MockerFixture):
    call = mocker.patch(
        "declarativex.executors.httpx.AsyncClient.send",
        side_effect=TimeoutException(
            0.1, httpx.Request("GET", "https://reqres.in/api/users")
        ),
    )
    sleep = mocker.patch("asyncio.sleep", MagicMock(wraps=asyncio.sleep))
    try:
        await client.get_users()
    except TimeoutException:
        pass
    else:
        raise AssertionError("Expected TimeoutException")

    assert call.call_count == 4
    assert 3 == len(
        [call[0][0] for call in sleep.call_args_list if call[0][0] == 0.1]
    )


def test_sync_retry(mocker: MockerFixture):
    call = mocker.patch(
        "declarativex.executors.httpx.Client.send",
        side_effect=TimeoutException(
            0.1, httpx.Request("GET", "https://reqres.in/api/users")
        ),
    )
    sleep = mocker.patch("time.sleep", MagicMock(wraps=time.sleep))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            sync_client.get_users()
        except TimeoutException:
            pass
        else:
            raise AssertionError("Expected TimeoutException")

    assert call.call_count == 4
    assert 3 == len(
        [call[0][0] for call in sleep.call_args_list if call[0][0] == 0.1]
    )
