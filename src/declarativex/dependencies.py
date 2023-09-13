import abc
import dataclasses
import enum
import inspect
import json
from string import Formatter
from typing import (
    Any,
    Callable,
    List,
    TYPE_CHECKING,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

from pydantic import BaseModel

from .compatibility import to_dict
from .exceptions import DependencyValidationError, MisconfiguredException
from .warnings import warn_no_type_hint

if TYPE_CHECKING:
    from .models import RawRequest


Value = TypeVar("Value")
Empty = type("Empty", (), {})()
EMPTY_VALUES = (Empty, Ellipsis, inspect.Parameter.empty)


class Location(str, enum.Enum):
    """Enum for dependency locations."""

    path = "path"
    query = "query"
    header = "header"
    cookie = "cookie"
    json = "json"
    json_field = "json_field"


class Dependency(abc.ABC):
    location: Location
    request_accessor: str = ""
    _field_name: str
    _value: Any

    def __init__(
        self,
        default: Any = Empty,
        field_name: Union[str, None] = None,
        type_hint: Union[Type[Value], None] = None,
    ):
        self.default = default
        self._overridden_field_name = field_name
        self._type_hint = type_hint

    @property
    def type_hint(self) -> Union[Type[Value], None]:
        return self._type_hint

    @type_hint.setter
    def type_hint(self, value: Union[Type[Value], None]) -> None:
        self._type_hint = value

    @property
    def field_name(self) -> str:
        return self._overridden_field_name or self._field_name

    @field_name.setter
    def field_name(self, value: str) -> None:
        self._field_name = value

    @property
    def value(self) -> Any:
        if self._value in EMPTY_VALUES:
            return self.default
        return self._value

    @value.setter
    def value(self, value: Any) -> None:
        self._value = self.validate(value)

    def validate(self, value: Any) -> Any:
        if self.type_hint:
            return self.__validate_type_hint(value)
        warn_no_type_hint(self.field_name)
        return value

    def __validate_type_hint(self, value: Any) -> Any:
        if get_origin(self.type_hint) is Union:
            return self.__validate_union_type_hint(value)
        if not isinstance(value, self.type_hint):  # type: ignore[arg-type]
            if value in EMPTY_VALUES and self.default not in EMPTY_VALUES:
                return value
            raise DependencyValidationError(
                expected_type=self.type_hint,  # type: ignore[arg-type]
                received_type=type(value)
            )
        return value

    def __validate_union_type_hint(self, value: Any) -> Any:
        args = get_args(self.type_hint)

        if value is None:
            if self.default in EMPTY_VALUES and type(None) not in args:
                raise DependencyValidationError(
                    expected_type=args, received_type=type(None)
                )
            return self.default if value not in EMPTY_VALUES else value

        if not any(isinstance(value, arg) for arg in args):
            raise DependencyValidationError(
                expected_type=args, received_type=type(value)
            )

        return value

    def modify_request(self, request: "RawRequest") -> "RawRequest":
        if self.value in EMPTY_VALUES:
            return request
        data = getattr(request, self.request_accessor)
        data[self.field_name] = self.value
        setattr(request, self.request_accessor, data)
        return request


class Path(Dependency):
    location = Location.path
    request_accessor = "path_params"


class Query(Dependency):
    location = Location.query
    request_accessor = "query_params"


class Header(Dependency):
    location = Location.header
    request_accessor = "headers"


class Cookie(Dependency):
    location = Location.cookie
    request_accessor = "cookies"


class JsonField(Dependency):
    location = Location.json_field
    request_accessor = "json"


class Json(Dependency):
    location = Location.json

    def modify_request(self, request: "RawRequest") -> "RawRequest":
        if isinstance(self.value, BaseModel):
            request.json = {**request.json, **to_dict(self.value)}
        elif dataclasses.is_dataclass(self.value):
            request.json = {**request.json, **dataclasses.asdict(self.value)}
        elif isinstance(self.value, dict):
            request.json = {**request.json, **self.value}
        elif isinstance(self.value, str):
            try:
                request.json = {**request.json, **json.loads(self.value)}
            except ValueError as exc:
                raise DependencyValidationError(
                    expected_type=self.type_hint,  # type: ignore[arg-type]
                    received_type=str,
                ) from exc
        return request


class RequestModifier:
    @staticmethod
    def __extract_variables_from_url_template(url_template: str) -> List[str]:
        return [
            field[1] for field in Formatter().parse(url_template) if field[1]
        ]

    @classmethod
    def prepare_request(
        cls, request: "RawRequest", func: Callable, **values
    ) -> "RawRequest":
        signature = inspect.signature(func)
        url_template_variables = cls.__extract_variables_from_url_template(
            request.url_template
        )
        dependencies = []
        for key, val in signature.parameters.items():
            if key in ["self", "cls"]:
                continue
            if issubclass(val.default.__class__, Dependency):
                dependency = val.default
            elif key in url_template_variables:
                dependency = Path(default=val.default)
            else:
                dependency = Query(default=val.default)
            dependency.type_hint = func.__annotations__.get(key, None)
            dependency.field_name = key
            dependency.value = values.get(key, Empty)
            dependencies.append(dependency)

        if request.method == "GET" and any(
            isinstance(dependency, (JsonField, Json))
            for dependency in dependencies
        ):
            raise MisconfiguredException(
                "BodyField and Json fields are not supported for GET requests"
            )

        for dependency in dependencies:
            request = dependency.modify_request(request)
        return request


__all__ = [
    "Dependency",
    "Path",
    "Query",
    "Header",
    "Cookie",
    "JsonField",
    "Json",
    "RequestModifier",
    "Empty",
]
