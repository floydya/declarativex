from typing import Any, Optional, TypeVar

from pydantic import BaseModel


class BaseParam:
    """
    Base class for declarative HTTP client parameters.

    Parameters:
        default (Any): Default value for the parameter.
        field_name (str | None):
            Name of the field to replace the keyword argument.
    """
    def __init__(
        self, default: Any = None, field_name: Optional[str] = None
    ) -> None:
        if default is Ellipsis:
            default = None
        self.default = default
        self.field_name = field_name

    @staticmethod
    def parse(value: Any) -> Any:
        return value


class Path(BaseParam):
    ...


class Query(BaseParam):
    ...


class BodyField(BaseParam):
    ...


class Json(BaseParam):

    @staticmethod
    def parse(value: Any) -> Any:
        from .compatibility import to_dict
        return to_dict(value) if isinstance(value, BaseModel) else value


ParamType = TypeVar("ParamType", bound=BaseParam)


__all__ = ["BaseParam", "Path", "Query", "BodyField", "Json", "ParamType"]
