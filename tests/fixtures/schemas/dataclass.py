import dataclasses

from typing import Generic, List, TypeVar


AnyModel = TypeVar("AnyModel")


@dataclasses.dataclass
class PaginatedResponse(Generic[AnyModel]):
    page: int
    per_page: int
    total: int
    total_pages: int
    data: List[AnyModel]


@dataclasses.dataclass
class SingleResponse(Generic[AnyModel]):
    data: AnyModel


@dataclasses.dataclass
class User:
    id: int
    email: str
    first_name: str
    last_name: str
    avatar: str


@dataclasses.dataclass
class BaseUserSchema:
    name: str
    job: str


@dataclasses.dataclass
class UserCreateResponse(BaseUserSchema):
    id: int
    createdAt: str


@dataclasses.dataclass
class UserUpdateResponse(BaseUserSchema):
    updatedAt: str


@dataclasses.dataclass
class AnyResource:
    id: int
    name: str
    year: int
    color: str
    pantone_value: str


@dataclasses.dataclass
class RegisterResponse:
    id: int
    token: str


@dataclasses.dataclass
class RegisterBadRequestResponse:
    error: str
