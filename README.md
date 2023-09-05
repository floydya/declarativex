# DeclarativeX

## Why DeclarativeX? 🤔

Tired of spelling out each HTTP step? Headers, JSON parsing, the whole shebang? Chill, `DeclarativeX` is here to simplify your life. Now you can focus on what actually matters — your business logic.

## Key Features 🗝️

- **Declarative Syntax**: Just slap on some decorators and you're good to go.
- **Data Validation**: Got Pydantic? We've got your back on robust data validation.
- **Async Support**: Async you said? Yep, we're all in.

## How to Get It 🛠

```bash
pip install declarativex
```

## The Basics 📚

### Param Types Explained 🤓

Here's the lowdown on the different param types:

- `default` - sets a default value.
- `field_name` - Changes the field name at the `Client` implementation level.

### 🛤️ Path

Pass data right into the URL path like so:

```python
class SomeClient(BaseClient):
    @get("/some/path/{uuid}/")
    def get_some_data(uuid: UUID = Path(...)):
     ...
```

But hey, if the arg name matches the path variable, that's your default.

So the example above equals:

```python
class SomeClient(BaseClient):
    @get("/some/path/{uuid}/")
    def get_some_data(uuid: UUID):
        ...
```

### 🔍 Query

Want URL query params? No biggie:

```python
class SomeClient(BaseClient):
    @get("/some/path/")
    def get_some_data(order_by: str = Query(default="name_asc", field_name="orderBy")):
        ...
```

> Goodbye, lowerCamelCase! Hello, Pythonic style! 🐍

If we had a snake_case `order_by` field in external API we deal with, the code will be like this:

```python
class SomeClient(BaseClient):
    @get("/some/path/")
    def get_some_data(order_by: str = "name_asc"):
        ...
```

### 📦 BodyField

Let's imagine, that we have two data sources and we need them to make a POST request with.

❓ What are you reaching for the dictionary for, huh?

You don't need to create a dictionary, that will contain the data, use `DeclarativeX`:

```python
class FooClient(declarativex.BaseClient):

    @post("/bar")
    def create_baz(foo: BodyField(...), baz: BodyField(...)) -> dict:
        ...


client = FooClient(base_url="https://example.com/")
```

Meanwhile, in the parallel ~~reality~~ file:

```python
def do_something():
    foo = fetch_from_db()
    baz = fetch_from_cache()
    client.create_baz(foo=foo, baz=baz)
```

If you've actually given in and made that dictionary, check out the next parameter type... Who did I even bother for?

### 📄 Json

Haha, so you did end up creating that damn dictionary, huh? Alright, now let's see how you're gonna use it:

```python
@post("/bar")
def create_baz(data: Json(...)) -> dict:
    ...

```

There you go, you've put it to use. Happy now? 😄

## Quick Examples 🚀

### 1️⃣ Basic GET Request

Fetch a todo item like a pro:

```python
from declarativex import BaseClient, get, Path

class TodoClient(BaseClient):
    @get("/todos/{id}")
    async def get_todo_by_id(self, id: int = Path(...)) -> dict:
        pass

todo_client = TodoClient("https://jsonplaceholder.typicode.com")
response = await todo_client.get_todo_by_id(1)
```

### 2️⃣ GET with Query Params

Here's how to get comments for a post:

```python
from declarativex import BaseClient, get, Query

class CommentClient(BaseClient):
    @get("/comments")
    async def get_comments(self, post_id: int = Query(...)) -> list:
        pass

comment_client = CommentClient("https://jsonplaceholder.typicode.com")
response = await comment_client.get_comments(post_id=1)
```

### 3️⃣ POST with JSON Body

Check out this POST request:

```python
from declarativex import BaseClient, post, Json

class PostClient(BaseClient):
    @post("/posts")
    async def create_post(self, data: dict = Json(...)) -> dict:
        pass

post_client = PostClient("https://jsonplaceholder.typicode.com")
response = await post_client.create_post(data={"title": "foo", "body": "bar", "userId": 1})
```

### 4️⃣ Timeout Handling

You can even set timeouts, because who's got time to wait?

```python
from declarativex import BaseClient, post, Json

class PostClient(BaseClient):
    @post("/delay/{delay}", timeout=3)
    async def create_post(self, delay: int) -> dict:
        pass

post_client = PostClient("https://jsonplaceholder.typicode.com")
response = await post_client.create_post(data={"title": "foo", "body": "bar", "userId": 1})
```

### Pydantic Love ❤️

Use Pydantic models for both input and output:

```python
import asyncio

from declarativex import BaseClient, post, Json
from pydantic import BaseModel


class MyPydanticModel(BaseModel):
    name: str
    age: int


class AsyncPydanticClient(BaseClient):
    @post("/some/path")
    async def post_something(self, data: MyPydanticModel = Json(...)) -> MyPydanticModel:
        pass


client = AsyncPydanticClient(base_url="https://example.com/")
asyncio.run(client.post_something(MyPydanticModel(name="John", age=42))
```

## Wrap Up 🌯

And there you have it — `DeclarativeX`. Making your HTTP requests easier, more Pythonic, and just plain better.

## Support the Creator 🙌
If you're digging DeclarativeX and want to give back, consider supporting the creator. Your contributions help keep this project alive and kicking!

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/E1E2OL196)

Every bit helps and is massively appreciated! 🌟
