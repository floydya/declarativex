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
pydantic_version = parse_version(pydantic.__version__)

if pydantic_version >= parse_version("2.0.0"):

    def parse_obj(pydantic_model: Type[M], obj: Any) -> M:
        return pydantic_model.model_validate(obj=obj)

    def parse_raw(pydantic_model: Type[M], json_data: Union[str, bytes]) -> M:
        return pydantic_model.model_validate_json(json_data=json_data)

    def to_dict(pydantic_obj: M, **kwargs) -> dict:
        return pydantic_obj.model_dump(**kwargs)

    def parse_obj_as(type_: Type[T], obj: Any) -> T:
        return pydantic.TypeAdapter(type_).validate_python(obj)

    class Field(Generic[ParamType], BaseModel):
        location: ParamType
        type: Any
        value: Any
        name: str

        model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

else:

    def parse_obj(pydantic_model: Type[M], obj: Any) -> M:
        return pydantic_model.parse_obj(obj=obj)

    def parse_raw(pydantic_model: Type[M], json_data: Union[str, bytes]) -> M:
        return pydantic_model.parse_raw(b=json_data)

    def to_dict(pydantic_obj: M, **kwargs) -> dict:
        return pydantic_obj.dict(**kwargs)

    def parse_obj_as(type_: Type[T], obj: Any) -> T:
        return pydantic.parse_obj_as(type_, obj)

    class Field(Generic[ParamType], BaseModel):  # type: ignore[no-redef]
        location: ParamType
        type: Any
        value: Any
        name: str

        class Config:
            arbitrary_types_allowed = True
