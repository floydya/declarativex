from typing import List, Optional, Union, get_args

import pytest

from src.declarativex import http, BaseClient, Query, Json, JsonField
from src.declarativex.dependencies import Empty
from src.declarativex.exceptions import (
    DependencyValidationError,
    MisconfiguredException,
)
from src.declarativex.warnings import DeclarativeWarning


def test_class_without_base_url():
    class Client(BaseClient):
        pass

    with pytest.raises(MisconfiguredException):
        _ = Client()


def test_endpoint_with_wrong_parameters():
    with pytest.raises(MisconfiguredException) as exc:

        @http("GET", "/test", default_headers=[{"x-test": "test"}])
        def endpoint(self):
            pass

    assert "default_headers must be a dictionary" == str(exc.value)

    with pytest.raises(MisconfiguredException) as exc:

        @http("GET", "/test", default_query_params=[{"x-test": "test"}])
        def endpoint(self):
            pass

    assert "default_query_params must be a dictionary" == str(exc.value)

    with pytest.raises(MisconfiguredException) as exc:

        @http("GET", "/test", middlewares={"x-test": "test"})
        def endpoint(self):
            pass

    assert "middlewares must be a list" == str(exc.value)

    with pytest.raises(MisconfiguredException) as exc:

        @http("GET", "/test", error_mappings=[{"x-test": "test"}])
        def endpoint(self):
            pass

    assert "error_mappings must be a dictionary" == str(exc.value)

    with pytest.raises(MisconfiguredException) as exc:

        @http(
            "TEST", "/test", base_url="https://jsonplaceholder.typicode.com/"
        )
        def endpoint(self):
            pass

    assert (
        "method must be one of ['DELETE', 'GET', 'PATCH', 'POST', 'PUT']"
        == str(exc.value)
    )

    with pytest.raises(MisconfiguredException) as exc:

        @http("GET", "/test", timeout=-2)
        def endpoint(self):
            pass

    assert "timeout must be a non-negative number" == str(exc.value)


def test_endpoint_wrong_type_hints():
    @http("GET", "/posts", base_url="https://jsonplaceholder.typicode.com/")
    def get_posts(userId: int = Query()) -> dict:
        pass

    with pytest.raises(DependencyValidationError) as exc:
        get_posts("1")
    assert str(
        DependencyValidationError(expected_type=int, received_type=str)
    ) == str(exc.value)

    with pytest.warns(DeclarativeWarning) as record:
        result = get_posts(1)

    assert str(record.list[0].message) == (
        DeclarativeWarning.LIST_RETURN_TYPE.format(t=dict.__name__)
    )
    assert isinstance(result, list)

    @http("GET", "/posts", base_url="https://jsonplaceholder.typicode.com/")
    def get_posts(userId=Query()) -> List[dict]:
        pass

    with pytest.warns(DeclarativeWarning) as record:
        result = get_posts(1)

    assert str(record.list[0].message) == (
        DeclarativeWarning.NO_TYPE_HINT.format(f="userId")
    )
    assert isinstance(result, list)
    assert len(result) == 10

    @http("GET", "/posts", base_url="https://jsonplaceholder.typicode.com/")
    def get_posts(userId: Optional[int] = Query()) -> List[dict]:
        pass

    with pytest.raises(DependencyValidationError) as exc:
        get_posts()

    assert str(
        DependencyValidationError(
            expected_type=get_args(Optional[int]), received_type=type(Empty)
        )
    ) == str(exc.value)

    @http("GET", "/posts", base_url="https://jsonplaceholder.typicode.com/")
    def get_posts(userId: Optional[int] = Query(default=1)) -> List[dict]:
        pass

    assert len(get_posts(None)) == 10

    @http("GET", "/posts", base_url="https://jsonplaceholder.typicode.com/")
    def get_posts(userId: Union[str, int]) -> List[dict]:
        pass

    with pytest.raises(DependencyValidationError) as exc:
        get_posts(None)

    assert str(
        DependencyValidationError(
            expected_type=get_args(Union[str, int]), received_type=type(None)
        )
    ) == str(exc.value)


def test_endpoint_default_empty_value():
    @http("get", "/posts", base_url="https://jsonplaceholder.typicode.com/")
    def get_posts(userId) -> List[dict]:
        pass
    with pytest.warns(DeclarativeWarning):
        assert len(get_posts(...)) == 100


@pytest.mark.parametrize("dependency", [JsonField, Json])
def test_get_endpoint_with_json_in_args(dependency):
    @http("get", "/posts", base_url="https://jsonplaceholder.typicode.com/")
    def get_posts(
        userId: Optional[int] = None, json: dict = dependency()
    ) -> List[dict]:
        pass

    with pytest.raises(MisconfiguredException) as exc:
        get_posts(1, {"test": "test"})

    assert (
        "BodyField and Json fields are not supported for GET requests"
        == str(exc.value)
    )
