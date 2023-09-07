import dataclasses
import importlib
from typing import Any, Union
from unittest import mock

import pytest

import src.declarativex.compatibility


class MockBaseModel:
    @classmethod
    def model_validate(cls, obj: dict) -> "MockBaseModel":
        return cls()  # pragma: no cover

    @classmethod
    def model_validate_json(
        cls, json_data: Union[str, bytes]
    ) -> "MockBaseModel":
        return cls()  # pragma: no cover

    def model_dump(self, **kwargs: Any) -> dict:
        return {"mock": "data"}  # pragma: no cover

    @classmethod
    def parse_obj(cls, obj: dict) -> "MockBaseModel":
        return cls()  # pragma: no cover

    @classmethod
    def parse_raw(cls, b: Union[str, bytes]) -> "MockBaseModel":
        return cls()  # pragma: no cover

    def dict(self, **kwargs: Any) -> dict:
        return {"mock": "data"}  # pragma: no cover


@pytest.fixture(scope="module")
def pydantic_mock() -> mock.MagicMock:
    with mock.patch(
        "src.declarativex.compatibility.BaseModel", new=MockBaseModel
    ):
        yield


@pytest.fixture(scope="session")
def pydantic_version_2() -> str:
    with mock.patch("pydantic.version.VERSION", "2.0.0"):
        importlib.reload(src.declarativex.compatibility)
        yield


@pytest.fixture(scope="session")
def pydantic_version_1() -> str:
    with mock.patch("pydantic.version.VERSION", "1.0.0"):
        importlib.reload(src.declarativex.compatibility)
        yield


@pytest.mark.usefixtures("pydantic_mock", "pydantic_version_2")
def test_parse_obj_for_version_2() -> None:
    result = src.declarativex.compatibility.parse_obj(
        MockBaseModel, {"test": "data"}
    )
    assert isinstance(result, MockBaseModel)


@pytest.mark.usefixtures("pydantic_mock", "pydantic_version_2")
def test_parse_raw_for_version_2() -> None:
    result = src.declarativex.compatibility.parse_raw(
        MockBaseModel, '{"test": "data"}'
    )
    assert isinstance(result, MockBaseModel)


@pytest.mark.usefixtures("pydantic_mock", "pydantic_version_2")
def test_to_dict_for_version_2() -> None:
    result = src.declarativex.compatibility.to_dict(
        MockBaseModel(), mock_data="data"
    )
    assert result == {"mock": "data"}


@pytest.mark.usefixtures("pydantic_mock", "pydantic_version_2")
def test_parse_obj_as_version_2() -> None:
    @dataclasses.dataclass
    class Data:
        test: str

    result = src.declarativex.compatibility.parse_obj_as(
        Data, {"test": "data"}
    )
    assert isinstance(result, Data)


@pytest.mark.usefixtures("pydantic_mock", "pydantic_version_1")
def test_parse_obj_for_version_1() -> None:
    result = src.declarativex.compatibility.parse_obj(
        MockBaseModel, {"test": "data"}
    )
    assert isinstance(result, MockBaseModel)


@pytest.mark.usefixtures("pydantic_mock", "pydantic_version_1")
def test_parse_raw_for_version_1() -> None:
    result = src.declarativex.compatibility.parse_raw(
        MockBaseModel, '{"test": "data"}'
    )
    assert isinstance(result, MockBaseModel)


@pytest.mark.usefixtures("pydantic_mock", "pydantic_version_1")
def test_to_dict_for_version_1() -> None:
    result = src.declarativex.compatibility.to_dict(
        MockBaseModel(), mock_data="data"
    )
    assert result == {"mock": "data"}


@pytest.mark.usefixtures("pydantic_mock", "pydantic_version_1")
def test_parse_obj_as_version_1() -> None:
    @dataclasses.dataclass
    class Data:
        test: str

    result = src.declarativex.compatibility.parse_obj_as(
        Data, {"test": "data"}
    )
    assert isinstance(result, Data)
