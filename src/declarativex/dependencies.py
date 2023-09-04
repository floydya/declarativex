from typing import Any, Optional

import pydantic


class BaseParam:
    def __init__(
        self, default: Optional[Any] = None, field_name: Optional[str] = None
    ) -> None:
        if default is Ellipsis:
            default = None
        self.default = default
        self.field_name = field_name


Path = type("Path", (BaseParam,), {})
Query = type("Query", (BaseParam,), {})
BodyField = type("BodyField", (BaseParam,), {})
Json = type("Json", (BaseParam,), {})
Timeout = pydantic.create_model("Timeout", seconds=(int, ...))


__all__ = ["BaseParam", "Path", "Query", "BodyField", "Json", "Timeout"]
