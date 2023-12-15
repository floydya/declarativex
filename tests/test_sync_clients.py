import json
import time
from json import JSONDecodeError
from unittest.mock import Mock, MagicMock

import httpx
import pytest
from httpx import Response, Proxy, URL
from pytest_mock import MockerFixture

from declarativex import http, BaseClient
from declarativex.exceptions import (
    DependencyValidationError,
    HTTPException,
    TimeoutException,
)
from .fixtures import (
    sync_dataclass_client,
    sync_pydantic_client,
    sync_dictionary_client,
    dataclass,
    pydantic,
)


@pytest.mark.parametrize(
    "client,response_type",
    [
        (sync_dataclass_client, dataclass.SingleResponse),
        (sync_pydantic_client, pydantic.SingleResponse),
        (sync_dictionary_client, dict),
    ],
)
def test_sync_get_user(client, response_type):
    user = client.get_user(1)
    assert isinstance(user, response_type)
    if isinstance(user, dict):
        assert user.get("data").get("id") == 1
    else:
        assert user.data.id == 1

    with pytest.raises(TimeoutException):
        _ = client.get_user(1, delay=3)

    _ = client.get_user(1, delay=2, timeout=3.0)


@pytest.mark.parametrize(
    "client,response_type",
    [
        (sync_dataclass_client, dataclass.PaginatedResponse),
        (sync_pydantic_client, pydantic.PaginatedResponse),
        (sync_dictionary_client, dict),
    ],
)
def test_sync_get_users(client, response_type):
    users = client.get_users()
    assert isinstance(users, response_type)
    if isinstance(users, dict):
        assert users.get("page") == 1
    else:
        assert users.page == 1

    with pytest.raises(TimeoutException):
        _ = client.get_users(delay=3)


@pytest.mark.parametrize(
    "client,body,response_type",
    [
        (
            sync_dataclass_client,
            dataclass.BaseUserSchema(name="John", job="worker"),
            dataclass.UserCreateResponse,
        ),
        (
            sync_pydantic_client,
            pydantic.BaseUserSchema(name="John", job="worker"),
            pydantic.UserCreateResponse,
        ),
        (sync_dictionary_client, dict(name="John", job="worker"), dict),
        (
            sync_dictionary_client,
            json.dumps({"name": "John", "job": "worker"}),
            dict,
        ),
    ],
)
def test_sync_create_user(client, body, response_type):
    user = client.create_user(user=body)
    assert isinstance(user, response_type)
    if isinstance(user, dict):
        assert "id" in user and "createdAt" in user
    else:
        assert user.id and user.createdAt

    time.sleep(1.5)

    if response_type is dict:
        with pytest.raises(DependencyValidationError) as err:
            _ = client.create_user(user="invalid json")

        assert isinstance(err.value.__cause__, JSONDecodeError)

    time.sleep(1.5)

    start_time = time.perf_counter()
    for i in range(3):
        client.create_user(user=body)
    elapsed = time.perf_counter() - start_time
    assert elapsed > 2


@pytest.mark.parametrize(
    "client,response_type",
    [
        (sync_dataclass_client, dataclass.UserUpdateResponse),
        (sync_pydantic_client, pydantic.UserUpdateResponse),
        (sync_dictionary_client, dict),
    ],
)
def test_sync_update_user(client, response_type):
    user = client.update_user(user_id=1, name="John", job="worker")
    assert isinstance(user, response_type)
    if isinstance(user, dict):
        assert "updatedAt" in user
    else:
        assert user.updatedAt


@pytest.mark.parametrize(
    "client",
    [
        sync_dataclass_client,
        sync_pydantic_client,
        sync_dictionary_client,
    ],
)
def test_sync_delete_user(client):
    response = client.delete_user(1)
    assert isinstance(response, httpx.Response)
    assert response.status_code == 204
    assert response.text == ""


@pytest.mark.parametrize(
    "client,response_type",
    [
        (sync_dataclass_client, dataclass.PaginatedResponse),
        (sync_pydantic_client, pydantic.PaginatedResponse),
        (sync_dictionary_client, dict),
    ],
)
def test_sync_get_resources_list(client, response_type):
    resources = client.get_resources()
    assert isinstance(resources, response_type)
    if isinstance(resources, dict):
        assert resources.get("page") == 1
    else:
        assert resources.page == 1


@pytest.mark.parametrize(
    "client,response_type,resource_type",
    [
        (
            sync_dataclass_client,
            dataclass.SingleResponse,
            dataclass.AnyResource,
        ),
        (sync_pydantic_client, pydantic.SingleResponse, pydantic.AnyResource),
        (sync_dictionary_client, dict, dict),
    ],
)
def test_sync_get_resource(client, response_type, resource_type):
    resource = client.get_resource(1)
    assert isinstance(resource, response_type)
    if isinstance(resource, dict):
        data = resource.get("data")
        assert isinstance(data, dict)
        assert data.get("id") == 1
    else:
        assert isinstance(resource.data, resource_type)
        assert resource.data.id == 1


@pytest.mark.parametrize(
    "client,response_type,error_type",
    [
        (
            sync_dataclass_client,
            dataclass.RegisterResponse,
            dataclass.RegisterBadRequestResponse,
        ),
        (
            sync_pydantic_client,
            pydantic.RegisterResponse,
            pydantic.RegisterBadRequestResponse,
        ),
        (sync_dictionary_client, dict, httpx.Response),
    ],
)
def test_sync_register(client, response_type, error_type):
    user = client.register(
        user={"email": "eve.holt@reqres.in", "password": "q1w2e3r4t5y6"},
        auth="Bearer test",
    )
    assert isinstance(user, response_type)
    if isinstance(user, dict):
        assert user.get("id") == 4
        assert user.get("token")
    else:
        assert user.id == 4
        assert user.token

    with pytest.raises(HTTPException) as exc:
        _ = client.register(
            user={"email": "test@testemail.com", "password": "q1w2e3r4t5y6"},
            auth="Bearer test",
        )

    assert isinstance(exc.value.response, error_type)
    assert "authorization" in exc.value.raw_request.headers
    assert exc.value.raw_request.headers["authorization"] == "Bearer test"
    assert exc.value.status_code == 400
    if error_type is httpx.Response:
        assert exc.value.response.json().get("error") == (
            "Note: Only defined users succeed registration"
        )
    else:
        assert exc.value.response.error == (
            "Note: Only defined users succeed registration"
        )


@pytest.mark.parametrize(
    "class_proxies,method_proxies,expected",
    [
        (
            {"http://": "http://127.0.0.1:2023"},
            {"https://": "https://127.0.0.1:2024"},
            {
                "http://": "http://127.0.0.1:2023",
                "https://": "https://127.0.0.1:2024",
            },
        ),
        (
            "http://127.0.0.1:2020",
            {"all://": "http://127.0.0.1:2021"},
            {
                "all://": "http://127.0.0.1:2021",
            },
        ),
        (
            {"all://": "http://127.0.0.1:2021"},
            "http://127.0.0.1:2022",
            {"all://": "http://127.0.0.1:2022"},
        ),
        (
            Proxy(url="http://127.0.0.1:2012"),
            URL(url="http://127.0.0.2:2013"),
            {"all://": "http://127.0.0.2:2013"},
        ),
        (
            URL(url="http://127.0.0.2:2013"),
            None,
            URL(url="http://127.0.0.2:2013"),
        ),
        (
            "http://127.0.0.1:2022",
            Proxy(url="http://127.0.0.1:2012"),
            {"all://": "http://127.0.0.1:2012"},
        ),
        (
            URL(url="http://127.0.0.2:2013"),
            URL(url="http://127.0.0.2:2014"),
            {"all://": "http://127.0.0.2:2014"},
        ),
    ],
)
def test_proxies(
    class_proxies, method_proxies, expected, mocker: MockerFixture
):
    httpx_client_mock = mocker.patch(
        "declarativex.executors.httpx.Client",
        MagicMock(),
    )
    httpx_client_mock.return_value.__enter__.return_value = Mock(
        send=Mock(
            return_value=Response(
                200,
                json={"dummy": "data"},
                request=Mock(
                    wraps=httpx.Request("GET", "https://reqres.in/api/users")
                ),
            )
        )
    )

    class DummyClient(BaseClient):
        proxies = class_proxies

        @http("GET", "api/users", proxies=method_proxies)
        def get_users(self) -> dict:
            ...

    client = DummyClient(base_url="https://reqres.in")
    client.get_users()
    assert httpx_client_mock.call_args_list[0][1]["proxies"] == expected
