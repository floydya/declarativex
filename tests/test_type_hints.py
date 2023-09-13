import sys

from pydantic import BaseModel

from src.declarativex import declare


if sys.version_info >= (3, 11):

    class Post(BaseModel):
        userId: int
        id: int
        title: str
        body: str

    class AnyEntity(BaseModel):
        id: str

    @declare("GET", "/posts", base_url="https://jsonplaceholder.typicode.com")
    def get_posts() -> list[dict]:
        pass

    @declare(
        "GET",
        "/posts/{post_id}",
        base_url="https://jsonplaceholder.typicode.com",
    )
    def get_post(post_id: int) -> Post | AnyEntity:
        pass

    @declare(
        "GET",
        "/posts/{post_id}",
        base_url="https://jsonplaceholder.typicode.com",
    )
    def get_post_reversed_return_type(post_id: int) -> AnyEntity | Post:
        pass

    def test_get_posts():
        posts = get_posts()
        assert isinstance(posts, list)
        assert isinstance(posts[0], dict)

    def test_get_post():
        post = get_post(1)
        assert isinstance(post, Post)
        assert post.id == 1

    def test_get_post_reversed_return_type():
        post = get_post(1)
        assert isinstance(post, Post)
        assert post.id == 1
