import warnings
from typing import Any, Type, TypeVar

import pydantic
from pydantic import BaseModel

with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=DeprecationWarning)
    from pkg_resources import parse_version


M = TypeVar("M", bound=BaseModel)
pydantic_version = parse_version(pydantic.__version__)

if pydantic_version >= parse_version("2.0.0"):

    def parse_obj(pydantic_model: Type[M], obj: Any) -> M:
        return pydantic_model.model_validate(obj=obj)

    def parse_raw(pydantic_model: Type[M], json_data: str | bytes) -> M:
        return pydantic_model.model_validate_json(json_data=json_data)

    def to_dict(pydantic_obj: M, **kwargs) -> dict:
        return pydantic_obj.model_dump(**kwargs)

else:

    def parse_obj(pydantic_model: Type[M], obj: Any) -> M:
        return pydantic_model.parse_obj(obj=obj)

    def parse_raw(pydantic_model: Type[M], json_data: str | bytes) -> M:
        return pydantic_model.parse_raw(b=json_data)

    def to_dict(pydantic_obj: M, **kwargs) -> dict:
        return pydantic_obj.dict(**kwargs)
