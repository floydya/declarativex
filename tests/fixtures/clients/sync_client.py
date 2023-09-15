from typing import TypeAlias, Union

from src.declarativex import (
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

from typing import Annotated


sync_dataclass_client = None
sync_pydantic_client = None
sync_dictionary_client = None


for schema in [dataclass, pydantic, None]:
    UserResponseSchema: TypeAlias = schema.SingleResponse[schema.User] if schema else dict
    UserListResponseSchema: TypeAlias = (
        schema.PaginatedResponse[schema.User] if schema else dict
    )
    CreateUserSchema: TypeAlias = schema.BaseUserSchema if schema else Union[dict, str]
    CreateUserResponseSchema: TypeAlias = schema.UserCreateResponse if schema else dict
    UpdateUserResponseSchema: TypeAlias = schema.UserUpdateResponse if schema else dict
    ResourcesListResponseSchema: TypeAlias = (
        schema.PaginatedResponse[schema.AnyResource] if schema else dict
    )
    ResourceResponseSchema: TypeAlias = (
        schema.SingleResponse[schema.AnyResource] if schema else dict
    )
    RegisterResponseSchema: TypeAlias = schema.RegisterResponse if schema else dict

    class SyncClientPydantic(BaseClient):
        base_url = "https://reqres.in/"

        @declare("GET", "api/users/{user_id}")
        def get_user(
            self,
            user_id: Annotated[int, Path],
            delay: int = 0,
            timeout: Annotated[float, Timeout()] = 2.0,
        ) -> UserResponseSchema:
            ...

        @declare("GET", "api/users", timeout=2)
        def get_users(
            self, delay: Annotated[int, Query()] = 0
        ) -> UserListResponseSchema:
            ...

        @rate_limiter(max_calls=1, interval=1)
        @declare("POST", "api/users")
        def create_user(
            self,
            user: Annotated[CreateUserSchema, Json()],
        ) -> CreateUserResponseSchema:
            ...

        @declare("PUT", "api/users/{user_id}")
        def update_user(
            self,
            user_id: int,
            name: Annotated[str, JsonField()],
            job: Annotated[str, JsonField()],
        ) -> UpdateUserResponseSchema:
            ...

        @declare("DELETE", "api/users/{user_id}")
        def delete_user(self, user_id: int):
            ...

        @declare("GET", "api/{resource}")
        def get_resources(
            self,
            resource_name: Annotated[
                str, Path(field_name="resource")
            ] = "unknown",
        ) -> ResourcesListResponseSchema:
            ...

        @declare("GET", "api/unknown/{resource_id}")
        def get_resource(self, resource_id: int) -> ResourceResponseSchema:
            ...

        @declare(
            "POST",
            "api/register",
            error_mappings={400: schema.RegisterBadRequestResponse}
            if schema
            else None,
        )
        def register(
            self,
            user: Annotated[dict, Json()],
            auth: Annotated[str, Header(name="Authorization")],
        ) -> RegisterResponseSchema:
            ...

    if schema == dataclass:
        sync_dataclass_client = SyncClientPydantic()
    elif schema == pydantic:
        sync_pydantic_client = SyncClientPydantic()
    elif schema is None:
        sync_dictionary_client = SyncClientPydantic()
