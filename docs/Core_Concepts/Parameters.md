# Param Types Explained 🤓

## A few words about params 😶

Here's the lowdown on the different kwargs:

`default`

:   The default value to use if there is no data passed to function, if not provided the field is required.

`field_name`

:   The name of the field to use, if nothing is passed, it will use the name of the function argument.



## Path 🛤️

Pass data right into the URL path like so:

```.py title="my_client.py" hl_lines="7"
from declarativex import declare, Path
from uuid import UUID


@declare("GET", "/some/path/{uuid}/")
def get_some_data(
    uuid: UUID = Path()
) -> dict:
    ...
```

But hey, if the arg name matches the path variable, that's your default.

So the example above equals:

```.py title="my_client.py" hl_lines="7"
from declarativex import declare, Path
from uuid import UUID


@declare("GET", "/some/path/{uuid}/")
def get_some_data(
    uuid: UUID
) -> dict:
    ...
```

## Query 🔍

Want URL query params? No biggie:

```.py title="my_client.py" hl_lines="6"
from declarativex import declare, Query


@declare("GET", "/some/path/")
def get_some_data(
    order_by: str = Query(default="name_asc", field_name="orderBy")
) -> dict:
    ...
```

!!! success
    Goodbye, lowerCamelCase! Hello, Pythonic style! 🐍

If we had a snake_case `order_by` field in external API we deal with, the code will be like this:

```.py title="my_client.py" hl_lines="6"
from declarativex import declare


@declare("GET", "/some/path/")
def get_some_data(
    order_by: str = "name_asc"
) -> dict:
    ...

```

## BodyField 📦

Let's imagine, that we have two data sources, and we need them to make a POST request with.

❓ What are you reaching for the dictionary for, huh?

You don't need to create a dictionary, that will contain the data, use `DeclarativeX`:

```.py title="my_client.py" hl_lines="9 10"
from declarativex import declare, BodyField


class FooClient(declarativex.BaseClient):
    base_url="https://example.com/"

    @declare("POST", "/bar")
    def create_baz(
        foo: str = BodyField(...), 
        baz: str = BodyField(...),
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

If you've actually given in and made that dictionary, check out the next parameter type... Who did I even bother for?

## Json 📄

Haha, so you did end up creating that damn dictionary, huh? Alright, now let's see how you're gonna use it:

```.py title="my_client.py" hl_lines="6"
from declarativex import declare, Json


@declare("POST", "/bar")
def create_baz(
    data: dict = Json(...)
) -> dict:
    ...
```

There you go, you've put it to use. Happy now? 😄
