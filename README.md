# DeclarativeX

## Description
DeclarativeX aims to make HTTP requests more declarative in Python. It uses Pydantic for data validation and Httpx for making the requests.

## Installation
```bash
pip install declarativex
```

## Usage
Here's a simple example:
```python
from declarativex import BaseClient, get, Path


class MyClient(BaseClient):
    @get("/some/path{id}")
    def get_something(self, id: int = Path(...)) -> dict:
        pass


client = MyClient(base_url="https://example.com/")
client.get_something(id=42)
```

Async with pydantic example:
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