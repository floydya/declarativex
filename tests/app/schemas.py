import dataclasses

from pydantic import BaseModel


class BasePost(BaseModel):
    userId: int
    title: str
    body: str


class Post(BasePost):
    id: int


class BaseComment(BaseModel):
    postId: int
    name: str
    email: str
    body: str


class Comment(BaseComment):
    id: int


class BaseTodo(BaseModel):
    userId: int
    title: str
    completed: bool


class Todo(BaseTodo):
    id: int


@dataclasses.dataclass
class BasePostDataclass:
    userId: int
    title: str
    body: str


@dataclasses.dataclass
class PostDataclass(BasePostDataclass):
    id: int


@dataclasses.dataclass
class BaseCommentDataclass:
    postId: int
    name: str
    email: str
    body: str


@dataclasses.dataclass
class CommentDataclass(BaseCommentDataclass):
    id: int


@dataclasses.dataclass
class BaseTodoDataclass:
    userId: int
    title: str
    completed: bool


@dataclasses.dataclass
class TodoDataclass(BaseTodoDataclass):
    id: int
