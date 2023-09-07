from pydantic import BaseModel


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
