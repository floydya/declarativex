---
title: Dependencies - Core Concepts in DeclarativeX
description: Learn about dependencies in DeclarativeX. Understand how to manage and inject dependencies into your HTTP clients.
---

# Dependencies Explained 🤓

This documentation primarily consists of classes that model various types of HTTP request dependencies, 
including query parameters, headers, cookies, and more. These dependencies are meant to modify and 
validate the incoming request before it hits the server.

## Dependency

You can override the default field name(that is picked from the function argument name) by passing `field_name` param.

All the dependencies are inherited from `Dependency` class.

## Path 🛤️

Pass data right into the URL path like so:

```.py title="my_client.py" hl_lines="1 9"
from typing import Annotated
from uuid import UUID

from declarativex import http, Path


@http("GET", "/some/path/{uuid}/")
def get_some_data(
    uuid: Annotated[UUID, Path]
) -> dict:
    ...
```

But hey, if the arg name matches the path variable, that's your default.

So the example above equals:

```.py title="my_client.py" hl_lines="7"
from declarativex import http, Path
from uuid import UUID


@http("GET", "/some/path/{uuid}/")
def get_some_data(
    uuid: UUID
) -> dict:
    ...
```

!!! note
    So, if you have a path variable with the same name as the function argument - `Path` will be used automatically.

## Query 🔍

Want URL query params? No biggie:

```.py title="my_client.py" hl_lines="1 8"
from typing import Annotated

from declarativex import http, Query


@http("GET", "/some/path/")
def get_some_data(
    order_by: Annotated[str, Query(field_name="orderBy")] = "name_asc"
) -> dict:
    ...
```

!!! success
    Goodbye, lowerCamelCase! Hello, Pythonic style! 🐍

If we had a snake_case `order_by` field in external API we deal with, the code will be like this:

```.py title="my_client.py" hl_lines="6"
from declarativex import http


@http("GET", "/some/path/")
def get_some_data(
    order_by: str = "name_asc"
) -> dict:
    ...

```

!!! note
    So, if you don't have a path variable with the same name as the function argument - `Query` will be used automatically.

## JsonField 📦

Let's imagine, that we have two data sources, and we need them to make a POST request with.

❓ What are you reaching for the dictionary for, huh?

You don't need to create a dictionary, that will contain the data, use `JsonField` dependency:

```.py title="my_client.py" hl_lines="1 11 12"
from typing import Annotated

from declarativex import http, JsonField


class FooClient(declarativex.BaseClient):
    base_url="https://example.com/"

    @http("POST", "/bar")
    def create_baz(
        foo: Annotated[str, JsonField], 
        baz: Annotated[str, JsonField],
    ) -> dict:
        ...


client = FooClient()
```

Meanwhile, in the parallel ~~reality~~ file:

```.py title="do_things.py" hl_lines="4"
def do_something():
    foo = fetch_from_db()
    baz = fetch_from_cache()
    client.create_baz(foo=foo, baz=baz)
```

!!! example
    It will be equal to:
    ```python
    any_http_lib.post("http://example.com/bar", {"foo": foo, "baz": baz})
    ```

If you've actually given in and made that dictionary, check out the next parameter type... Who did I even bother for?

## Json 📄

Haha, so you did end up creating that damn dictionary, huh? Alright, now let's see how you're gonna use it:

Just, to let you know, there is no `field_name` param for `Json` dependency, because it is not needed.

```.py title="my_client.py" hl_lines="1 8"
from typing import Annotated

from declarativex import http, Json


@http("POST", "/bar")
def create_baz(
    data: Annotated[dict, Json]
) -> dict:
    ...
```

There you go, you've put it to use. Happy now? 😄

## Header 🎩

The difference between `Header` and any other dependency is that `Header` has only a `name` param. 
And it is required.

So, you can use them like this:

```.py title="my_client.py" hl_lines="1 8"
from typing import Annotated

from declarativex import http, Header


@http("POST", "/bar")
def create_baz(
    x_foo: Annotated[str, Header(name="X-Foo")]
) -> dict:
    ...
```

!!! danger
    The `name` param is required for headers, because usually custom headers have `-` char.


## Cookie 🍪

You can use them like this:

```.py title="my_client.py" hl_lines="1 8"
from typing import Annotated

from declarativex import http, Cookie


@http("POST", "/bar")
def create_baz(
    session_id: Annotated[str, Cookie]
) -> dict:
    ...
```


## Timeout ⏱️

You can define a changeable timeout using dependency:

```.py title="my_client.py" hl_lines="1 8"
from typing import Annotated

from declarativex import http, Timeout


@http("POST", "/bar")
def create_baz(
    timeout: Annotated[int, Timeout]
) -> dict:
    ...
```

!!! note
    If you need to define a constant timeout, you can use `timeout` param in `@http` decorator.
