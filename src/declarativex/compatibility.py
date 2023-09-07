import warnings
from typing import Any, Generic, Type, TypeVar, Union

import pydantic
from pydantic import BaseModel

from .dependencies import ParamType


with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=DeprecationWarning)
    from pkg_resources import parse_version


M = TypeVar("M", bound=BaseModel)
T = TypeVar("T")

pydantic_version = parse_version(pydantic.version.VERSION)


def parse_obj(pydantic_model: Type[M], obj: Any) -> M:
    if pydantic_version >= parse_version("2.0.0"):
        return pydantic_model.model_validate(obj=obj)
    return pydantic_model.parse_obj(obj=obj)


def parse_raw(pydantic_model: Type[M], json_data: Union[str, bytes]) -> M:
    if pydantic_version >= parse_version("2.0.0"):
        return pydantic_model.model_validate_json(json_data=json_data)
    return pydantic_model.parse_raw(b=json_data)


def to_dict(pydantic_obj: M, **kwargs) -> dict:
    if pydantic_version >= parse_version("2.0.0"):
        return pydantic_obj.model_dump(**kwargs)
    return pydantic_obj.dict(**kwargs)


def parse_obj_as(type_: Type[T], obj: Any) -> T:
    if pydantic_version >= parse_version("2.0.0"):
        return pydantic.TypeAdapter(type_).validate_python(obj)
    return pydantic.parse_obj_as(type_, obj)


class Field(Generic[ParamType], BaseModel):
    location: ParamType
    type: Any
    value: Any
    name: str

    if pydantic_version >= parse_version("2.0.0"):
        model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)
    else:
        class Config:
            arbitrary_types_allowed = True
