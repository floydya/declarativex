from typing import Annotated, List, Optional, Union, get_args

import pytest

from declarativex import http, BaseClient, Query, Json, JsonField
from declarativex.exceptions import (
    AnnotationException,
    DependencyValidationError,
    MisconfiguredException,
    UnprocessableEntityException,
)
from declarativex.warnings import DeclarativeWarning


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
    def get_posts(userId: Annotated[int, Query]) -> dict:
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
    def get_posts(userId: Annotated[int, Query] = 1) -> List[dict]:
        pass

    assert len(get_posts()) == 10

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
        assert len(get_posts(...)) == 0


@pytest.mark.parametrize("dependency", [JsonField, Json])
def test_get_endpoint_with_json_in_args(dependency):
    @http("get", "/posts", base_url="https://jsonplaceholder.typicode.com/")
    def get_posts(
        data: Annotated[dict, dependency],
        userId: Optional[int] = None,
    ) -> List[dict]:
        pass

    with pytest.raises(MisconfiguredException) as exc:
        get_posts({"test": "test"}, 1)

    assert (
        f"{dependency.__name__} dependency is not "
        "available for GET method."
        == str(exc.value)
    )


def test_unprocessable_entity_exception():
    @http("get", "/", base_url="https://jsonplaceholder.typicode.com/")
    def get_data() -> dict:
        pass

    with pytest.raises(UnprocessableEntityException) as exc:
        get_data()

    assert str(exc.value) == (
        "Failed to parse response. Status code: 200. "
        "You can access the raw response using the `response` attribute."
    )


def test_annotation_exception():
    @http("get", "/", base_url="https://jsonplaceholder.typicode.com/")
    def get_data(userId: Annotated[int, "test"]) -> dict:
        pass

    with pytest.raises(AnnotationException) as exc:
        get_data(1)

    assert str(exc.value) == (
        "Annotation typing.Annotated[int, 'test'] is not supported. "
        "Use Annotated[type, Dependency] instead."
    )
