from typing import Optional

import pytest
from pydantic import BaseModel

from src.declarativex import (
    BaseClient,
    BodyField,
    Json,
    Path,
    Query,
    get,
    post,
)


class BaseTodo(BaseModel):
    userId: int
    title: str
    completed: bool


class Todo(BaseTodo):
    id: int


class Comment(BaseModel):
    postId: int
    id: int
    name: str
    email: str
    body: str


class TodoClient(BaseClient):
    @get("/todos/{id}")
    async def get_todo_by_id_raw(self, id: int) -> dict:
        ...  # pragma: no cover

    @get("/todos/{id}")
    async def get_todo_by_id_pydantic(self, id: int = Path(...)) -> Todo:
        ...  # pragma: no cover

    @get("/comments")
    async def get_comments_raw(self, postId: int = Query(...)) -> list[dict]:
        ...  # pragma: no cover

    @get("/posts/{postId}/comments")
    async def get_comments_value_error_path(
        self, postId: Optional[int] = Path(...)
    ) -> list[Comment]:
        ...  # pragma: no cover

    @get("/comments")
    async def get_comments_pydantic(
        self, postId: Optional[int] = 1
    ) -> list[Comment]:
        ...  # pragma: no cover

    @post("/posts")
    async def create_post(
        self,
        title: str = BodyField(...),
        body: str = BodyField(...),
        userId: int = BodyField(...),
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

    @post("/posts")
    async def create_post_pydantic(
        self,
        body: BaseTodo = Json(...),
    ) -> dict:
        ...  # pragma: no cover

    @post("/posts")
    async def create_post_mixed(
        self, body: dict = Json(...), userId: int = BodyField(...)
    ) -> dict:
        ...  # pragma: no cover


class SlowClient(BaseClient):
    @get("/delay/{delay}", timeout=1)
    def get_data_from_slow_endpoint(self, delay: int, query_delay: int):
        ...  # pragma: no cover

    @get("/delay/{delay}", timeout=1)
    async def async_get_data_from_slow_endpoint(
        self,
        delay: int = Path(...),
        query_delay: int = Query(field_name="delay"),
    ):
        ...  # pragma: no cover


class TestAsyncTodoClient:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = TodoClient("https://jsonplaceholder.typicode.com")

    @pytest.mark.asyncio
    async def test_get_todo_by_id_raw(self):
        todo = await self.client.get_todo_by_id_raw(id=1)
        assert isinstance(todo, dict)
        assert todo["id"] == 1

    @pytest.mark.asyncio
    async def test_get_todo_by_id_pydantic(self):
        todo = await self.client.get_todo_by_id_pydantic(id=1)
        assert isinstance(todo, Todo)
        assert todo.id == 1
        assert todo.title == "delectus aut autem"
        assert todo.completed is False
        assert todo.userId == 1

    @pytest.mark.asyncio
    async def test_get_comments_raw(self):
        comments = await self.client.get_comments_raw()
        assert isinstance(comments, list)
        assert len(comments) == 500

    @pytest.mark.asyncio
    async def test_get_comments_value_error_path(self):
        with pytest.raises(ValueError) as err:
            await self.client.get_comments_value_error_path()
        assert (
            str(err.value)
            == "Parameter with key='postId' is required and has no default"
        )

    @pytest.mark.asyncio
    async def test_get_comments_pydantic(self):
        comments = await self.client.get_comments_pydantic(postId=1)
        assert isinstance(comments, list), comments
        assert len(comments) == 5
        assert all(
            isinstance(comment, Comment) for comment in comments
        ), comments

    @pytest.mark.asyncio
    async def test_create_post(self):
        created_post = await self.client.create_post(
            title="foo",
            body="bar",
            userId=1,
        )
        assert isinstance(created_post, dict)
        assert created_post["id"] == 101

    @pytest.mark.asyncio
    async def test_create_post_pydantic(self):
        created_post = await self.client.create_post_pydantic(
            body=BaseTodo(
                userId=1,
                title="foo",
                completed=False,
            )
        )
        assert isinstance(created_post, dict)
        assert created_post["id"] == 101

    @pytest.mark.asyncio
    async def test_create_post_mixed(self):
        created_post = await self.client.create_post_mixed(
            body={
                "title": "foo",
                "completed": False,
            },
            userId=1,
        )
        assert isinstance(created_post, dict)
        assert created_post["id"] == 101


class TestSlowClient:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = SlowClient("https://httpbin.org")

    def test_sync_get_data_from_slow_endpoint(self):
        response = self.client.get_data_from_slow_endpoint(
            delay=0, query_delay=0
        )
        assert response["args"]["query_delay"] == "0"

    def test_sync_get_data_from_slow_endpoint_timeout(self):
        with pytest.raises(TimeoutError) as err:
            self.client.get_data_from_slow_endpoint(delay=3)
        assert str(err.value) == "Request timed out after 1 seconds"

    @pytest.mark.asyncio
    async def test_async_get_data_from_slow_endpoint(self):
        response = await self.client.async_get_data_from_slow_endpoint(
            delay=0, query_delay=0
        )
        assert response["args"]["delay"] == "0"

    @pytest.mark.asyncio
    async def test_async_get_data_from_slow_endpoint_timeout(self):
        with pytest.raises(TimeoutError) as err:
            await self.client.async_get_data_from_slow_endpoint(delay=3)
        assert str(err.value) == "Request timed out after 1 seconds"
