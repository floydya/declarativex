import asyncio
import json
import time
from json import JSONDecodeError

import httpx
import pytest

from src.declarativex.exceptions import (
    DependencyValidationError,
    HTTPException,
    TimeoutException,
)
from .fixtures import (
    async_dataclass_client,
    async_pydantic_client,
    async_dictionary_client,
    dataclass,
    pydantic,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "client,response_type",
    [
        (async_dataclass_client, dataclass.SingleResponse),
        (async_pydantic_client, pydantic.SingleResponse),
        (async_dictionary_client, dict),
    ],
)
async def test_async_get_user(client, response_type):
    user = await client.get_user(1)
    assert isinstance(user, response_type)
    if isinstance(user, dict):
        assert user.get("data").get("id") == 1
    else:
        assert user.data.id == 1

    with pytest.raises(TimeoutException):
        _ = await client.get_user(1, delay=3)

    _ = await client.get_user(1, delay=2, timeout=3.0)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "client,response_type",
    [
        (async_dataclass_client, dataclass.PaginatedResponse),
        (async_pydantic_client, pydantic.PaginatedResponse),
        (async_dictionary_client, dict),
    ],
)
async def test_async_get_users(client, response_type):
    users = await client.get_users()
    assert isinstance(users, response_type)
    if isinstance(users, dict):
        assert users.get("page") == 1
    else:
        assert users.page == 1

    with pytest.raises(TimeoutException):
        _ = await client.get_users(delay=3)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "client,body,response_type",
    [
        (
            async_dataclass_client,
            dataclass.BaseUserSchema(name="John", job="worker"),
            dataclass.UserCreateResponse,
        ),
        (
            async_pydantic_client,
            pydantic.BaseUserSchema(name="John", job="worker"),
            pydantic.UserCreateResponse,
        ),
        (async_dictionary_client, dict(name="John", job="worker"), dict),
        (
            async_dictionary_client,
            json.dumps({"name": "John", "job": "worker"}),
            dict,
        ),
    ],
)
async def test_async_create_user(client, body, response_type):
    user = await client.create_user(user=body)
    assert isinstance(user, response_type)
    if isinstance(user, dict):
        assert "id" in user and "createdAt" in user
    else:
        assert user.id and user.createdAt

    await asyncio.sleep(1.5)

    if response_type is dict:
        with pytest.raises(DependencyValidationError) as err:
            _ = await client.create_user(user="invalid json")

        assert isinstance(err.value.__cause__, JSONDecodeError)

    await asyncio.sleep(1.5)

    start_time = time.perf_counter()
    for i in range(3):
        await client.create_user(user=body)
    elapsed = time.perf_counter() - start_time
    assert elapsed > 2


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "client,response_type",
    [
        (async_dataclass_client, dataclass.UserUpdateResponse),
        (async_pydantic_client, pydantic.UserUpdateResponse),
        (async_dictionary_client, dict),
    ],
)
async def test_async_update_user(client, response_type):
    user = await client.update_user(user_id=1, name="John", job="worker")
    assert isinstance(user, response_type)
    if isinstance(user, dict):
        assert "updatedAt" in user
    else:
        assert user.updatedAt


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "client",
    [
        async_dataclass_client,
        async_pydantic_client,
        async_dictionary_client,
    ],
)
async def test_async_delete_user(client):
    response = await client.delete_user(1)
    assert isinstance(response, httpx.Response)
    assert response.status_code == 204


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "client,response_type",
    [
        (async_dataclass_client, dataclass.PaginatedResponse),
        (async_pydantic_client, pydantic.PaginatedResponse),
        (async_dictionary_client, dict),
    ],
)
async def test_async_get_resources_list(
    client, response_type
):
    resources = await client.get_resources()
    assert isinstance(resources, response_type)
    if isinstance(resources, dict):
        assert resources.get("page") == 1
    else:
        assert resources.page == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "client,response_type,resource_type",
    [
        (
            async_dataclass_client,
            dataclass.SingleResponse,
            dataclass.AnyResource,
        ),
        (async_pydantic_client, pydantic.SingleResponse, pydantic.AnyResource),
        (async_dictionary_client, dict, dict),
    ],
)
async def test_async_get_resource(
    client, response_type, resource_type
):
    resource = await client.get_resource(1)
    assert isinstance(resource, response_type)
    if isinstance(resource, dict):
        data = resource.get("data")
        assert isinstance(data, dict)
        assert data.get("id") == 1
    else:
        assert isinstance(resource.data, resource_type)
        assert resource.data.id == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "client,response_type,error_type",
    [
        (
            async_dataclass_client,
            dataclass.RegisterResponse,
            dataclass.RegisterBadRequestResponse,
        ),
        (
            async_pydantic_client,
            pydantic.RegisterResponse,
            pydantic.RegisterBadRequestResponse,
        ),
        (async_dictionary_client, dict, httpx.Response),
    ],
)
async def test_async_register(
    client, response_type, error_type
):
    user = await client.register(
        user={"email": "eve.holt@reqres.in", "password": "q1w2e3r4t5y6"},
        auth="Bearer test"
    )
    assert isinstance(user, response_type)
    if isinstance(user, dict):
        assert user.get("id") == 4
        assert user.get("token")
    else:
        assert user.id == 4
        assert user.token

    with pytest.raises(HTTPException) as exc:
        _ = await client.register(
            user={"email": "test@testemail.com", "password": "q1w2e3r4t5y6"},
            auth="Bearer test",
        )

    assert isinstance(exc.value.response, error_type)
    assert exc.value.status_code == 400
    assert "authorization" in exc.value.raw_request.headers
    assert exc.value.raw_request.headers["authorization"] == "Bearer test"
    if error_type is httpx.Response:
        assert exc.value.response.json().get("error") == (
            "Note: Only defined users succeed registration"
        )
    else:
        assert exc.value.response.error == (
            "Note: Only defined users succeed registration"
        )
