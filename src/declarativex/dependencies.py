import dataclasses
import inspect
import json
import warnings
from typing import (
    Any,
    Generic,
    Optional,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

from pydantic import BaseModel

from .compatibility import to_dict
from .exceptions import DependencyValidationError

Value = TypeVar("Value")
empty = inspect.Parameter.empty


class Dependency(Generic[Value]):
    _value: Any
    required: bool = False
    """
    Base class for declarative HTTP client parameters.

    Parameters:
        default (Any): Default value for the parameter.
        field_name (str | None):
            Name of the field to replace the keyword argument.
    """

    field_name: str
    _type: Type[Value]
    value: Value

    def __init__(
        self, default: Any = empty, field_name: Optional[str] = None
    ) -> None:
        if default is Ellipsis:
            default = empty
        self.default_value = default
        self._override_field_name = field_name

    def prepare(
        self, field_name: str, type_hint: Type, value: Any
    ) -> "Dependency":
        self.field_name = (
            self._override_field_name
            if self._override_field_name
            else field_name
        )
        self._type = type_hint
        value = self.validate(
            type_hint=type_hint, field_name=field_name, value=value
        )
        self.value = self.parse(value)
        return self

    def validate(self, type_hint: Type, field_name: str, value: Any) -> Any:
        if type_hint is None:
            warnings.warn(
                "Type hint for parameter with "
                f"name='{field_name}' is not specified. "
                "This is not recommended as it may "
                "lead to unexpected behaviour. "
                "Consider specifying a type hint for the parameter.",
                stacklevel=3,
            )
            return value

        # Checks if the type_hint is a Union type
        if get_origin(type_hint) is Union:
            # Gets the arguments for the Union type
            args = get_args(type_hint)

            # Special handling for Optional (which is just Union[T, None])
            if type(None) in args:
                args = tuple(t for t in args if not isinstance(t, type(None)))

                if value is None:
                    if self.default_value is not empty:
                        return self.default_value
                    return value
            elif value is None:
                raise DependencyValidationError(
                    expected_type=args,
                    received_type=type(value),
                )

            if not any(isinstance(value, arg) for arg in args):
                raise DependencyValidationError(
                    expected_type=args, received_type=type(value)
                )

            return value

        if not isinstance(value, type_hint):
            if value is None:
                raise DependencyValidationError(
                    expected_type=type_hint,
                    received_type=type(value),
                )
            raise DependencyValidationError(
                expected_type=type_hint, received_type=type(value)
            )

        return value

    @staticmethod
    def parse(value: Value) -> Any:
        return str(value)


class Path(Dependency):
    _value: str
    required: bool = True


class Query(Dependency):
    _value: str


class BodyField(Dependency):
    _value: dict | str | int | float | bool | None


class Json(Dependency):
    _value: dict

    @staticmethod
    def parse(value: Any) -> dict:
        if isinstance(value, BaseModel):
            return to_dict(value)
        if dataclasses.is_dataclass(value):
            return dataclasses.asdict(value)
        if isinstance(value, str):
            return json.loads(value)
        return value


ParamType = TypeVar("ParamType", bound=Dependency)


__all__ = [
    "Dependency",
    "Path",
    "Query",
    "BodyField",
    "Json",
    "ParamType",
    "empty",
]
