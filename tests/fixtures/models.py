import dataclasses

from pydantic import BaseModel


@dataclasses.dataclass
class BaseTodoDataClass:
    userId: int
    title: str
    completed: bool


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
