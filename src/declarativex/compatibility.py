import warnings
from typing import Any, Generic, Type, TypeVar, Union

import pydantic
from pydantic import BaseModel

from .dependencies import ParamType


M = TypeVar("M", bound=BaseModel)
T = TypeVar("T")


def parse_obj(pydantic_model: Type[M], obj: Any) -> M:
    with warnings.catch_warnings():  # pragma: no cover
        warnings.simplefilter("ignore", category=DeprecationWarning)
        return pydantic_model.parse_obj(obj=obj)


def parse_raw(pydantic_model: Type[M], json_data: Union[str, bytes]) -> M:
    with warnings.catch_warnings():  # pragma: no cover
        warnings.simplefilter("ignore", category=DeprecationWarning)
        return pydantic_model.parse_raw(b=json_data)


def to_dict(pydantic_obj: M, **kwargs) -> dict:
    with warnings.catch_warnings():  # pragma: no cover
        warnings.simplefilter("ignore", category=DeprecationWarning)
        return pydantic_obj.dict(**kwargs)


def parse_obj_as(type_: Type[T], obj: Any) -> T:
    with warnings.catch_warnings():  # pragma: no cover
        warnings.simplefilter("ignore", category=DeprecationWarning)
        return pydantic.parse_obj_as(type_, obj)


with warnings.catch_warnings():  # pragma: no cover
    warnings.simplefilter("ignore", category=DeprecationWarning)

    class Field(Generic[ParamType], BaseModel):
        location: ParamType
        type: Any
        value: Any
        name: str

        class Config:
            arbitrary_types_allowed = True
