import pytest

from src.declarativex import BaseClient, declare, JsonField, Json
from src.declarativex.exceptions import (
    MisconfiguredException,
    DependencyValidationError,
    TimeoutException,
)
from src.declarativex.methods import SUPPORTED_METHODS
from tests.fixtures.clients import (
    SlowClient,
    TodoClient,
    get_todo_by_id_raw,
    sync_get_todo_by_id_raw,
)
from tests.fixtures.models import Comment, Todo, BaseTodo, BaseTodoDataClass


class TestAsyncTodoClient:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = TodoClient()

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
        with pytest.raises(DependencyValidationError) as err:
            await self.client.get_comments_raw()

        assert str(err.value) == (
            "Value of type NoneType is not supported. Expected type: int. "
            "Specify a default value or use Optional[int] instead."
        )

    @pytest.mark.asyncio
    async def test_get_comments_pydantic(self):
        comments = await self.client.get_comments_pydantic(post_id=1)
        assert isinstance(comments, list)
        assert len(comments) == 5
        assert all(isinstance(comment, Comment) for comment in comments)

    @pytest.mark.asyncio
    async def test_create_post(self):
        created_post = await self.client.create_post(
            title="foo",
            body="bar",
            user_id=1,
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
    async def test_create_post_dataclass(self):
        created_post = await self.client.create_post_dataclass(
            body=BaseTodoDataClass(
                userId=1,
                title="foo",
                completed=False,
            )
        )
        assert isinstance(created_post, dict)
        assert created_post["id"] == 101

    @pytest.mark.asyncio
    async def test_misconfigured_create_post(self):
        with pytest.raises(DependencyValidationError) as err:
            await self.client.misconfigured_create_post(body=None)

        assert str(err.value) == (
            "Value of type NoneType is not supported. "
            "Expected one of: ['BaseTodo', 'dict']. "
            "Specify a default value or use Optional"
            "[typing.Union[tests.fixtures.models.BaseTodo, dict]] instead."
        )

    @pytest.mark.asyncio
    async def test_misconfigured_create_post_without_default(self):
        with pytest.raises(DependencyValidationError) as err:
            await self.client.misconfigured_create_post_without_default(
                body=None
            )

        assert str(err.value) == (
            "Value of type NoneType is not supported. "
            "Expected type: BaseTodo. "
            "Specify a default value or use "
            "Optional[BaseTodo] instead."
        )

    @pytest.mark.asyncio
    async def test_misconfigured_create_post_without_default_str_val(self):
        with pytest.raises(DependencyValidationError) as err:
            await self.client.misconfigured_create_post_without_default(
                body="test"
            )

        assert str(err.value) == (
            "Value of type str is not supported. Expected type: BaseTodo."
        )

    @pytest.mark.asyncio
    async def test_misconfigured_create_post_but_with_default(self):
        created_post = (
            await self.client.misconfigured_create_post_but_with_default()
        )
        assert isinstance(created_post, dict)
        assert created_post == {"id": 101, "data": "test"}

    @pytest.mark.asyncio
    async def test_misconfigured_create_post_invalid_type(self):
        with pytest.raises(DependencyValidationError) as err:
            await self.client.misconfigured_create_post_but_with_default(
                body="test"
            )

        assert str(err.value) == (
            "Value of type str is not supported. "
            "Expected one of: ['BaseTodo', 'dict', 'NoneType']."
        )

    @pytest.mark.asyncio
    async def test_update_post_mixed(self):
        created_post = await self.client.update_post_mixed(
            post_id=1,
            body={
                "title": "foo",
                "completed": False,
            },
            user_id=1,
        )
        assert isinstance(created_post, dict)
        assert created_post["id"] == 1

    @pytest.mark.asyncio
    async def test_update_post(self):
        updated_post = await self.client.update_post(
            post_id=1,
            body={
                "title": "foo",
                "completed": False,
            },
        )
        assert isinstance(updated_post, dict)
        assert updated_post["id"] == 1

    @pytest.mark.asyncio
    async def test_delete_post(self):
        deleted_post = await self.client.delete_post(post_id=1)
        assert isinstance(deleted_post, dict)
        assert deleted_post == {}


class TestSlowClient:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = SlowClient()

    def test_sync_get_data_from_slow_endpoint(self):
        response = self.client.get_data_from_slow_endpoint(
            delay=0, query_delay=0
        )
        assert response["args"]["query_delay"] == "0"

    def test_sync_get_data_from_slow_endpoint_timeout(self):
        with pytest.raises(TimeoutException) as err:
            self.client.get_data_from_slow_endpoint(delay=3)
        assert str(err.value) == (
            f"Request timed out after {2} seconds: "
            f"GET https://httpbin.org/delay/3"
        )

    @pytest.mark.asyncio
    async def test_async_get_data_from_slow_endpoint(self):
        response = await self.client.async_get_data_from_slow_endpoint(
            delay=0, query_delay=0
        )
        assert response["args"]["delay"] == "0"

    @pytest.mark.asyncio
    async def test_async_get_data_from_slow_endpoint_timeout(self):
        with pytest.raises(TimeoutException) as err:
            await self.client.async_get_data_from_slow_endpoint(delay=3)
        assert str(err.value) == (
            f"Request timed out after {1} seconds: "
            f"GET https://httpbin.org/delay/3"
        )


class TestMethodClient:
    @pytest.mark.asyncio
    async def test_get_todo_by_id_raw(self):
        response = await get_todo_by_id_raw(id=1)
        assert isinstance(response, dict)
        assert response["id"] == 1

    def test_sync_get_todo_by_id_raw(self):
        response = sync_get_todo_by_id_raw(1)
        assert isinstance(response, Todo)
        assert response.id == 1

    @pytest.mark.asyncio
    async def test_wrong_method(self):
        with pytest.raises(ValueError) as err:

            @declare(
                "TEST",
                "/todos/{id}",
                base_url="https://jsonplaceholder.typicode.com",
            )
            async def test_method(id: int):  # pragma: no cover
                ...

        assert str(err.value) == (
            f"Unsupported method: TEST. "
            f"Supported methods: {SUPPORTED_METHODS}"
        )


class TestBaseClient:
    def test_client_with_no_base_url(self):
        class Client(BaseClient):
            pass

        with pytest.raises(MisconfiguredException) as err:
            _ = Client()
        assert str(err.value) == "base_url is required"

    @pytest.mark.parametrize("field", [JsonField(...), Json(...)])
    def test_get_with_bodyfield_parameter(self, field):
        with pytest.raises(MisconfiguredException) as err:

            @declare(
                "GET",
                "/todos/{id}",
                base_url="https://jsonplaceholder.typicode.com",
            )
            def test_method(id: int, body: str = field):
                ...  # pragma: no cover

        assert str(err.value) == (
            "BodyField and Json fields are not supported for GET requests"
        )

    def test_get_with_invalid_return_type(self):
        @declare(
            "GET",
            "/todos",
            base_url="https://jsonplaceholder.typicode.com",
        )
        def test_method() -> Todo:
            ...  # pragma: no cover

        with pytest.warns(
            Warning,
            match=(
                "Provide a correct return type for "
                "your method, response is a list"
            ),
        ):
            data = test_method()

        assert isinstance(data, list)

    def test_get_with_no_return_type(self):
        with pytest.warns(
            Warning,
            match=(
                r"You must specify return type for your method\. "
                r"Example\: def test_method\(\.\.\.\) \-\> dict\: \.\.\."
            ),
        ):

            @declare(
                "GET",
                "/todos",
                base_url="https://jsonplaceholder.typicode.com",
            )
            def test_method():
                ...  # pragma: no cover

    def test_get_with_no_argument_type(self):
        @declare(
            "GET",
            "/todos/{id}",
            base_url="https://jsonplaceholder.typicode.com",
        )
        def test_method(id) -> dict:
            ...  # pragma: no cover

        with pytest.warns(
            Warning,
            match=(
                r"Type hint missing for \'id\'\. "
                r"Could lead to unexpected behaviour\."
            ),
        ):
            test_method(1)
