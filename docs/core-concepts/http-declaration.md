---
title: HTTP Declaration - Core Concepts in DeclarativeX
description: Learn the fundamentals of HTTP declaration in DeclarativeX. Understand how to define HTTP methods and endpoints effectively.
---

# HTTP declaration

DeclarativeX supports two ways of declaring clients: class-based and function-based.

Both are equally powerful and flexible, so it's up to you to decide which one to use.

## `#!python @http` decorator

The `#!python @http` decorator is the core of DeclarativeX. It's used to declare endpoints and specify their parameters.

### Syntax

=== "Sync"
    ```python
    @http(method, path, *, base_url, timeout, default_headers, default_query_params, middlewares)
    def method_name() -> dict:
        ...
    ```

=== "Async"
    ```python
    @http(method, path, *, base_url, timeout, default_headers, default_query_params, middlewares)
    async def method_name() -> dict:
        ...
    ```

!!! tip
    Sync and async functions are supported. Just define your function as `async` and you're good to go.


!!! note "Keyword-only arguments"
    All arguments after `path` are keyword-only arguments, so you must specify them by name.


### Supported methods

DeclarativeX currently supports the following HTTP methods:

- `GET`
- `POST`
- `PUT`
- `PATCH`
- `DELETE`

More HTTP methods will be added in the future.

!!! note "Case" 
    The HTTP method is case-insensitive, so you can use either `Get` or `get`.


!!! danger "Unsupported methods"
    If you will try to use unsupported HTTP method, you will get [MisconfiguredException](../api/exceptions.md#misconfiguredexception) exception at the runtime.


### Declare parameters

This table outlines the arguments you can pass to the decorator, detailing their type, 
whether they're required or optional, and what each argument is for.

#### Positional arguments

|           Name           |       Type       |           Required            |    Arg type    | Description                                                       |
|:------------------------:|:----------------:|:-----------------------------:|:--------------:|-------------------------------------------------------------------|
|         `method`         |  `#!python str`  |              Yes              |    Position    | Specifies the HTTP method (e.g., GET, POST, PUT) you want to use. |
|          `path`          |  `#!python str`  |              Yes              |   Position    | Defines the API endpoint path you're hitting.                     |


#### Keyword-only arguments

|          Name          |                      Type                      |              Required               |    Arg type    | Description                                                        |
|:----------------------:|:----------------------------------------------:|:-----------------------------------:|:--------------:|--------------------------------------------------------------------|
|       `base_url`       |                 `#!python str`                 | [Not always](#base_url "See below") |    Keyword     | Sets the base URL for the request.                                 |
|       `timeout`        |                 `#!python int`                 |    No, default: `#!python None`     |    Keyword     | The timeout to use.                                                |
|         `auth`         | `#!python declarativex.Auth` |    No, default: `#!python None`     |    Keyword     | The [auth instance](./auth.md) to use.                             | 
|   `default_headers`    |                `#!python dict`                 |    No, default: `#!python None`     |    Keyword     | The headers to use with every request.                             |
| `default_query_params` |                `#!python dict`                 |    No, default: `#!python None`     |    Keyword     | The params to use with every request.                              |
|     `middlewares`      | `#!python list`  |    No, default: `#!python None`     |    Keyword     | The [middlewares](middlewares.md) to use with every request.       |
|    `error_mappings`    | `#!python dict`  |    No, default: `#!python None`     |    Keyword     | The [error mappings](error-mappings.md) to use with every request. |
| `proxies` | `#!python dict | str | None | URL | Proxy` |   No, default: `#!python None`     |    Keyword     | The [proxies](https://www.python-httpx.org/advanced/#http-proxying) to use with every request. |

<div id="base_url" markdown>
!!! danger "`base_url`"
    This is necessary if the method is not part of a class that already specifies it.

    If you don't specify `base_url` in function-based declaration, you will get [MisconfiguredException](../api/exceptions.md#misconfiguredexception) exception at the runtime.
</div>

### Priority of the parameters resolution

The priority of the parameters is as follows:

1. Pick parameter from the decorator.
2. Pick parameter from the class.
3. If both are specified, merge them.

!!! info "Priority"
    Decorator parameters have **higher** priority and will __overwrite__ the same values of class parameter


### Return Type

You can use any of the custom dataclasses, Pydantic models or built-in types to parse the response automatically.

!!! warning "-> dict"
    If you don't specify a return type, the decorator will return a `httpx.Response` object.
    But, your IDE will not be able to detect the type of the response, so it's recommended to specify the return type.

!!! tip "explicitly specifying httpx.Response return type"
    Specifying `httpx.Respose` will both return unprocessed `httpx.Response` object and 
    preserve type hint information for IDE.

### Class-based declaration

Class-based declaration is the most common way to declare clients. It's also the most flexible one.

Use the `BaseClient` class as a base class for your client and declare methods using the `http` decorator.


#### Example

=== "Sync"

    ```.python title="my_client.py" hl_lines="10"
    from declarativex import BaseClient, http
    
    
    class MyClient(BaseClient):
        base_url = "https://example.com"
        default_query_params = {"api_key": "123456"}
        default_headers = {"X-Trace": "<hash>"}
    
        @http("GET", "/users/{user_id}", timeout=10)
        def get_user(self, user_id: int) -> dict:
            ...
    
    
    my_client = MyClient()
    user: dict = my_client.get_user(user_id=1)
    ```

=== "Async"

    ```.python title="my_client.py" hl_lines="12"
    import asyncio

    from declarativex import BaseClient, http
    
    
    class MyClient(BaseClient):
        base_url = "https://example.com"
        default_query_params = {"api_key": "123456"}
        default_headers = {"X-Trace": "<hash>"}
    
        @http("GET", "/users/{user_id}", timeout=10)
        async def get_user(self, user_id: int) -> dict:
            ...
    
    
    my_client = MyClient()
    user: dict = asyncio.run(my_client.get_user(user_id=1))
    ```

!!! danger "Class-based declaration"
    If you're using class-based declaration, you must pass `self` as the first argument to the method.

    It will be used to get the `base_url`, `default_query_params`, `default_headers` and other values.


### Function-based declaration


Function-based declaration is a great alternative to class-based declaration. It's more concise and doesn't require
you to create a class. Commonly used for simple clients with one endpoint.

#### Example

=== "Sync"
    ```.python title="my_client.py" hl_lines="12"
    from declarativex import http
    
    
    @http(
        "GET", 
        "/users/{user_id}", 
        base_url"https://example.com",
        timeout=10,
        default_headers={"X-Trace": "<hash>"},
        default_query_params={"api_key": "123456"}
    )
    def get_user(user_id: int) -> dict:
        ...
    ```

=== "Async"
    ```.python title="my_client.py" hl_lines="14"
    import asyncio

    from declarativex import http
    
    
    @http(
        "GET", 
        "/users/{user_id}", 
        base_url"https://example.com",
        timeout=10,
        default_headers={"X-Trace": "<hash>"},
        default_query_params={"api_key": "123456"}
    )
    def get_user(user_id: int) -> dict:
        ...

    user: dict = asyncio.run(get_user(user_id=1))
    ```

!!! note "Function-based declaration"
    
    If you're using function-based declaration, you don't need to add `self` as first argument.
    The parameters of the decorator will be used to get the `base_url`, `default_query_params` and `default_headers` values.
