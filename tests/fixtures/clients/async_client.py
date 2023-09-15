from typing import Annotated
from typing import Union

from declarativex import (
    BaseClient,
    declare,
    JsonField,
    rate_limiter,
    Json,
    Path,
    Timeout,
    Query,
    Header,
)
from tests.fixtures.schemas import dataclass, pydantic

async_dataclass_client = None
async_pydantic_client = None
async_dictionary_client = None


for schema in [dataclass, pydantic, None]:
    UserResponseSchema = schema.SingleResponse[schema.User] if schema else dict
    UserListResponseSchema = (
        schema.PaginatedResponse[schema.User] if schema else dict
    )
    CreateUserSchema = schema.BaseUserSchema if schema else Union[dict, str]
    CreateUserResponseSchema = schema.UserCreateResponse if schema else dict
    UpdateUserResponseSchema = schema.UserUpdateResponse if schema else dict
    ResourcesListResponseSchema = (
        schema.PaginatedResponse[schema.AnyResource] if schema else dict
    )
    ResourceResponseSchema = (
        schema.SingleResponse[schema.AnyResource] if schema else dict
    )
    RegisterResponseSchema = schema.RegisterResponse if schema else dict

    class AsyncClientPydantic(BaseClient):
        base_url = "https://reqres.in/"

        @declare("GET", "api/users/{user_id}")
        async def get_user(
            self,
            user_id: Annotated[int, Path],
            delay: int = 0,
            timeout: Annotated[float, Timeout()] = 2.0,
        ) -> UserResponseSchema:
            ...

        @declare("GET", "api/users", timeout=2)
        async def get_users(
            self, delay: Annotated[int, Query()] = 0
        ) -> UserListResponseSchema:
            ...

        @rate_limiter(max_calls=1, interval=1)
        @declare("POST", "api/users")
        async def create_user(
            self,
            user: Annotated[CreateUserSchema, Json()],
        ) -> CreateUserResponseSchema:
            ...

        @declare("PUT", "api/users/{user_id}")
        async def update_user(
            self,
            user_id: int,
            name: Annotated[str, JsonField()],
            job: Annotated[str, JsonField()],
        ) -> UpdateUserResponseSchema:
            ...

        @declare("DELETE", "api/users/{user_id}")
        async def delete_user(self, user_id: int):
            ...

        @declare("GET", "api/{resource}")
        async def get_resources(
            self,
            resource_name: Annotated[
                str, Path(field_name="resource")
            ] = "unknown",
        ) -> ResourcesListResponseSchema:
            ...

        @declare("GET", "api/unknown/{resource_id}")
        async def get_resource(
            self, resource_id: int
        ) -> ResourceResponseSchema:
            ...

        @declare(
            "POST",
            "api/register",
            error_mappings={400: schema.RegisterBadRequestResponse}
            if schema
            else None,
        )
        async def register(
            self,
            user: Annotated[dict, Json()],
            auth: Annotated[str, Header(name="Authorization")],
        ) -> RegisterResponseSchema:
            ...

    if schema == dataclass:
        async_dataclass_client = AsyncClientPydantic()
    elif schema == pydantic:
        async_pydantic_client = AsyncClientPydantic()
    elif schema is None:
        async_dictionary_client = AsyncClientPydantic()
