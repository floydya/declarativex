# BaseClient: The Heart of DeclarativeX ❤️

## Introduction

Hey, welcome to the `BaseClient` section! If you're wondering what makes DeclarativeX tick, you've come to the right
place. `BaseClient` is the core class that powers all the magic. Let's dive in!

## Initialization

First things first, let's see how to initialize a `BaseClient`:

```{.python title="my_client.py"}
from declarativex import BaseClient

class MyClient(BaseClient):
    pass
```

That's it! You've just created your first `BaseClient`. 🎉

## Attributes

### `base_url`

The `base_url` is where all the magic starts. It's the root URL that your client will use for all requests.

=== "Using class attribute"
    ```{.python title="my_client.py"}
    from declarativex import BaseClient


    class MyClient(BaseClient):
        base_url = "https://api.example.com"


    client = MyClient()
    ```
    !!! tip
        Prefer this approach if you don't need to change the `base_url` at runtime.

=== "Using __init__ argument"
    ```{.python title="my_client.py"}
    from declarativex import BaseClient


    class MyClient(BaseClient):
        pass


    client = MyClient(base_url="https://api.example.com")
    ```

=== "Overriding constructor"
    ```{.python title="my_client.py"}
    from declarativex import BaseClient


    class MyClient(BaseClient):
        def __init__(self, *args, **kwargs):
            kwargs["base_url"] = "https://api.example.com"
            super().__init__(*args, **kwargs)


    client = MyClient()
    ```

### `default_headers`

Need to add some custom headers? No worries, BaseClient has got you covered.

=== "Using class attribute"
    ```{.python title="my_client.py"}
    from declarativex import BaseClient

    from myapp.settings import settings


    class MyClient(BaseClient):
        base_url = "https://api.example.com"
        default_headers = {"Authorization": f"Bearer {settings.EXAMPLE_API_TOKEN}"}


    client = MyClient()
    ```
    !!! tip
        Prefer this approach if you don't need to change the headers at runtime.

=== "Using __init__ argument"
    ```{.python title="my_client.py"}
    from declarativex import BaseClient

    from myapp.settings import settings


    class MyClient(BaseClient):
        pass


    client = MyClient(
        base_url="https://api.example.com",
        default_headers={"Authorization": f"Bearer {settings.EXAMPLE_API_TOKEN}"
    )
    ```

=== "Overriding constructor"
    ```{.python title="my_client.py"}
    from declarativex import BaseClient

    from myapp.settings import settings


    class MyClient(BaseClient):
        def __init__(self, *args, **kwargs):
            kwargs["base_url"] = "https://api.example.com"
            kwargs["default_headers"] = {"Authorization": "Bearer <token>"}
            super().__init__(*args, **kwargs)


    client = MyClient()
    ```

### `default_query_params`

Do you have Steam API integration :melting_face:? Then you know how annoying it is to add the `key` parameter to every
request. Well, `BaseClient` has got you covered.

=== "Using class attribute"
    ```{.python title="my_client.py"}
    from declarativex import BaseClient

    from myapp.settings import settings


    class MyClient(BaseClient):
        base_url = "https://api.example.com"
        default_query_params = {"key": settings.STEAM_API_KEY}


    client = MyClient()
    ```
    !!! tip
        Prefer this approach if you don't need to change the `key` at runtime.

=== "Using __init__ argument"
    ```{.python title="my_client.py"}
    from declarativex import BaseClient

    from myapp.settings import settings


    class MyClient(BaseClient):
        pass


    client = MyClient(
        base_url="https://api.example.com",
        default_query_params={"key": settings.STEAM_API_KEY}
    )
    ```

=== "Overriding constructor"
    ```{.python title="my_client.py"}
    from declarativex import BaseClient
    
    from myapp.settings import settings


    class MyClient(BaseClient):
        def __init__(self, *args, **kwargs):
            kwargs["base_url"] = "https://api.example.com"
            kwargs["default_query_params"] = {"key": settings.STEAM_API_KEY}
            super().__init__(*args, **kwargs)


    client = MyClient()
    ```

### `middlewares`

Middlewares are a powerful tool that allows you to modify requests and responses.

=== "Using class attribute"
    ```{.python title="my_client.py"}
    from declarativex import BaseClient

    from myapp.middlewares import MyMiddleware


    class MyClient(BaseClient):
        base_url = "https://api.example.com"
        middlewares = [MyMiddleware()]


    client = MyClient()
    ```

=== "Using __init__ argument"
    ```{.python title="my_client.py"}
    from declarativex import BaseClient

    from myapp.middlewares import MyMiddleware


    class MyClient(BaseClient):
        pass


    client = MyClient(
        base_url="https://api.example.com",
        middlewares=[MyMiddleware()]
    )
    ```

!!! tip
    They are covered in detail in the [Middlewares](./middlewares.md) section.


### `error_mappings`

Error mappings are a powerful tool that allows you to map HTTP status codes to response parser.

You can use `pydantic.BaseModel`, `dataclass` or `TypedDict` to parse the response.

=== "Using class attribute"
    ```{.python title="my_client.py"}
    from declarativex import BaseClient
    from pydantic import BaseModel

    from myapp.middlewares import MyMiddleware


    class BadRequestResponseSchema(BaseModel):
        message: str


    class MyClient(BaseClient):
        base_url = "https://api.example.com"
        error_mappings = {
            400: BadRequestResponseSchema
        }


    client = MyClient()
    ```

=== "Using __init__ argument"
    ```{.python title="my_client.py"}
    from declarativex import BaseClient
    from pydantic import BaseModel

    from myapp.middlewares import MyMiddleware


    class BadRequestResponseSchema(BaseModel):
        message: str


    class MyClient(BaseClient):
        pass


    client = MyClient(
        base_url="https://api.example.com",
        error_mappings={400: BadRequestResponseSchema}
    )
    ```


!!! tip
    More information you can find in the [Error mappings](./error-mappings.md) section.


## Wrapping Up

So there you have it, the `BaseClient` in all its glory. It's the cornerstone of DeclarativeX, designed to make your
life easier and your code cleaner.

Feel like diving deeper? Check out the [HTTP Declaration](./http-declaration.md) and [Dependencies](./dependencies.md) sections next.
