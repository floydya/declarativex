from typing import Any, Optional


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


class Path(BaseParam):
    ...


class Query(BaseParam):
    ...


class BodyField(BaseParam):
    ...


class Json(BaseParam):
    ...


__all__ = ["BaseParam", "Path", "Query", "BodyField", "Json"]
