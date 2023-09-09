import dataclasses
import inspect
import json
import warnings
from typing import (
    Any,
    Type,
    TypeVar,
    Union,
    Optional,
    Generic,
    get_origin,
    get_args,
)

from pydantic import BaseModel

from .compatibility import to_dict
from .exceptions import DependencyValidationError

Value = TypeVar("Value")
empty = inspect.Parameter.empty


class Dependency(Generic[Value]):
    """Base class for declarative HTTP client parameters."""

    def __init__(
        self, default: Any = empty, field_name: Optional[str] = None
    ) -> None:
        self.default_value = default if default is not Ellipsis else empty
        self.field_name: str = field_name  # type: ignore[assignment]
        self._type: Optional[Type[Value]] = None
        self.value: Optional[Value] = None

    def prepare(
        self, field_name: str, type_hint: Type[Value], value: Any
    ) -> "Dependency":
        self.field_name = self.field_name or field_name
        self._type = type_hint
        self.value = self._parse(self._validate(type_hint, value))
        return self

    def _validate(self, type_hint: Optional[Type[Value]], value: Any) -> Any:
        if not type_hint:
            warnings.warn(
                f"Type hint missing for '{self.field_name}'. "
                "Could lead to unexpected behaviour.",
                stacklevel=3,
            )
            return value
        if get_origin(type_hint) is Union:
            return self._validate_union_type(type_hint, value)
        if not isinstance(value, type_hint):
            raise DependencyValidationError(
                expected_type=type_hint, received_type=type(value)
            )
        return value

    def _validate_union_type(self, type_hint: Type[Value], value: Any) -> Any:
        args = get_args(type_hint)

        if value is None:
            if self.default_value is empty and type(None) not in args:
                raise DependencyValidationError(
                    expected_type=args, received_type=type(None)
                )
            return (
                self.default_value
                if self.default_value is not empty
                else value
            )

        if not any(isinstance(value, arg) for arg in args):
            raise DependencyValidationError(
                expected_type=args, received_type=type(value)
            )

        return value

    def _parse(self, value: Value) -> Any:
        return str(value)


class StringDependency(Dependency[str]):
    """Dependency that expects a string value."""

    def _parse(self, value: str) -> Optional[str]:
        return str(value) if value is not None else None


class AnyDependency(Dependency[Value]):
    """Dependency that can accept any value."""


class DictDependency(Dependency[dict]):
    """Dependency that expects a dict value."""

    def _parse(self, value: Any) -> dict:
        if isinstance(value, BaseModel):
            return to_dict(value)
        if dataclasses.is_dataclass(value):
            return dataclasses.asdict(value)
        if isinstance(value, str):
            return json.loads(value)
        return value


class Path(StringDependency):
    pass


class Query(StringDependency):
    pass


class JsonField(AnyDependency):
    pass


class Header(StringDependency):
    def __init__(self, header_name: str, default: Any = empty) -> None:
        super().__init__(default=default, field_name=header_name)


class Cookie(StringDependency):
    def __init__(self, cookie_name: str, default: Any = empty) -> None:
        super().__init__(default=default, field_name=cookie_name)


class Json(DictDependency):
    pass


class FormData(Json):
    pass


ParamType = TypeVar("ParamType", bound=Dependency)

__all__ = [
    "Dependency",
    "Path",
    "Query",
    "JsonField",
    "Json",
    "Header",
    "Cookie",
    "FormData",
    "ParamType",
    "empty",
]
