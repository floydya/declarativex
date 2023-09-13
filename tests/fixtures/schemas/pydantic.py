import datetime
import warnings
from typing import Generic, List, TypeVar

from pydantic import BaseModel, AnyHttpUrl
from pydantic.generics import GenericModel

AnyModel = TypeVar("AnyModel", bound=BaseModel)


with warnings.catch_warnings():
    warnings.simplefilter("ignore")

    class PaginatedResponse(GenericModel, Generic[AnyModel]):
        page: int
        per_page: int
        total: int
        total_pages: int
        data: List[AnyModel] = []

        class Config:
            arbitrary_types_allowed = True

    class SingleResponse(GenericModel, Generic[AnyModel]):
        data: AnyModel

        class Config:
            arbitrary_types_allowed = True


class User(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    avatar: AnyHttpUrl


class BaseUserSchema(BaseModel):
    name: str
    job: str


class UserCreateResponse(BaseUserSchema):
    id: int
    createdAt: datetime.datetime


class UserUpdateResponse(BaseUserSchema):
    updatedAt: datetime.datetime


class AnyResource(BaseModel):
    id: int
    name: str
    year: int
    color: str
    pantone_value: str


class RegisterResponse(BaseModel):
    id: int
    token: str


class RegisterBadRequestResponse(BaseModel):
    error: str
