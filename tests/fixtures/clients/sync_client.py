from typing import Union

from src.declarativex import (
    BaseClient,
    declare,
    JsonField,
    rate_limiter,
    Json,
    Path,
)
from tests.fixtures.schemas import dataclass, pydantic

sync_dataclass_client = None
sync_pydantic_client = None
sync_dictionary_client = None


for schema in [dataclass, pydantic, None]:

    class SyncClientPydantic(BaseClient):
        base_url = "https://reqres.in/"

        @declare("GET", "api/users/{user_id}")
        def get_user(
            self, user_id: int
        ) -> schema.SingleResponse[schema.User] if schema else dict:
            ...

        @declare("GET", "api/users", timeout=2)
        def get_users(
            self, delay: int = 0
        ) -> schema.PaginatedResponse[schema.User] if schema else dict:
            ...

        @rate_limiter(max_calls=1, interval=1)
        @declare("POST", "api/users")
        def create_user(
            self,
            user: schema.BaseUserSchema
            if schema
            else Union[dict, str] = Json(),
        ) -> schema.UserCreateResponse if schema else dict:
            ...

        @declare("PUT", "api/users/{user_id}")
        def update_user(
            self, user_id: int, name: str = JsonField(), job: str = JsonField()
        ) -> schema.UserUpdateResponse if schema else dict:
            ...

        @declare("DELETE", "api/users/{user_id}")
        def delete_user(self, user_id: int):
            ...

        @declare("GET", "api/{resource}")
        def get_resources(
            self,
            resource_name: str = Path(
                default="unknown", field_name="resource"
            ),
        ) -> schema.PaginatedResponse[schema.AnyResource] if schema else dict:
            ...

        @declare("GET", "api/unknown/{resource_id}")
        def get_resource(
            self, resource_id: int
        ) -> schema.SingleResponse[schema.AnyResource] if schema else dict:
            ...

        @declare(
            "POST",
            "api/register",
            error_mappings={400: schema.RegisterBadRequestResponse}
            if schema
            else None,
        )
        def register(
            self, user: dict = Json()
        ) -> schema.RegisterResponse if schema else dict:
            ...

    if schema == dataclass:
        sync_dataclass_client = SyncClientPydantic()
    elif schema == pydantic:
        sync_pydantic_client = SyncClientPydantic()
    elif schema is None:
        sync_dictionary_client = SyncClientPydantic()
