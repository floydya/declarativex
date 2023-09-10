from typing import List, Optional, Union

from src.declarativex import (
    BaseClient,
    declare,
    Path,
    Query,
    JsonField,
    Json,
)
from tests.app.schemas import *


class TodoClient(BaseClient):
    base_url = "https://jsonplaceholder.typicode.com"

    @declare("GET", "/todos/{id}")
    async def get_todo_by_id_raw(self, id: int) -> dict:
        ...  # pragma: no cover

    @declare("GET", "/todos/{id}")
    async def get_todo_by_id_pydantic(self, id: int = Path(...)) -> Todo:
        ...  # pragma: no cover

    @declare("GET", "/comments")
    async def get_comments_raw(
        self, post_id: int = Query(field_name="postId")
    ) -> List[dict]:
        ...  # pragma: no cover

    @declare("GET", "/comments")
    async def get_comments_pydantic(
        self, post_id: int = Query(field_name="postId")
    ) -> List[Comment]:
        ...  # pragma: no cover

    @declare("POST", "/posts")
    async def create_post(
        self,
        title: str = JsonField(...),
        body: str = JsonField(...),
        user_id: int = JsonField(field_name="userId"),
    ) -> dict:
        """
        It will produce a request:
        POST /posts
        {
            "title": "foo",
            "body": "bar",
            "userId": 1
        }
        """
        ...  # pragma: no cover

    @declare("POST", "/posts")
    async def misconfigured_create_post(
        self,
        body: Union[BaseTodo, dict] = Json(...),
    ) -> dict:
        ...  # pragma: no cover

    @declare("POST", "/posts")
    async def misconfigured_create_post_without_default(
        self,
        body: BaseTodo = Json(...),
    ) -> dict:
        ...  # pragma: no cover

    @declare("POST", "/posts")
    async def misconfigured_create_post_but_with_default(
        self,
        body: Optional[Union[BasePost, dict]] = Json(
            default=BasePost(userId=1, title="foo", body="bar")
        ),
    ) -> dict:
        ...  # pragma: no cover

    @declare("POST", "/posts")
    async def create_post_pydantic(
        self,
        body: BasePost = Json(...),
    ) -> dict:
        ...  # pragma: no cover

    @declare("POST", "/posts")
    async def create_post_dataclass(
        self,
        body: BasePostDataclass = Json(...),
    ) -> dict:
        ...  # pragma: no cover

    @declare("PATCH", "/posts/{postId}")
    async def update_post_mixed(
        self,
        post_id: int = Path(field_name="postId"),
        data: dict = Json(...),
        user_id: int = JsonField(field_name="userId"),
    ) -> dict:
        ...  # pragma: no cover

    @declare("PUT", "/posts/{postId}")
    async def update_post(
        self, post_id: int = Path(field_name="postId"), body: dict = Json(...)
    ) -> dict:
        ...  # pragma: no cover

    @declare("DELETE", "/posts/{postId}")
    async def delete_post(
        self, post_id: int = Path(field_name="postId")
    ) -> dict:
        ...  # pragma: no cover


class SlowClient(BaseClient):
    base_url = "https://httpbin.org"

    @declare("GET", "/delay/{delay}", timeout=2)
    def get_data_from_slow_endpoint(
        self, delay: int, query_delay: Optional[int]
    ) -> dict:
        ...  # pragma: no cover

    @declare("GET", "/delay/{delay}", timeout=2)
    async def async_get_data_from_slow_endpoint(
        self,
        delay: int,
        query_delay: Optional[int],
    ) -> dict:
        ...  # pragma: no cover


@declare("GET", "/todos/{id}", base_url="https://jsonplaceholder.typicode.com")
async def get_todo_by_id_raw(id: int) -> dict:
    ...  # pragma: no cover


@declare("GET", "/todos/{id}", base_url="https://jsonplaceholder.typicode.com")
def sync_get_todo_by_id_raw(id: int) -> Todo:
    ...  # pragma: no cover
