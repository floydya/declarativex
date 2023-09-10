# Client declaration

DeclarativeX supports two ways of declaring clients: class-based and function-based.

Both are equally powerful and flexible, so it's up to you to decide which one to use.

## `#!python @declare` decorator

The `#!python @declare` decorator is the core of DeclarativeX. It's used to declare endpoints and specify their parameters.

### Syntax

```python
@declare(method, path, *, base_url, timeout, default_headers, default_query_params, middlewares)
def method_name() -> dict:
    ...
```

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
    If you will try to use unsupported HTTP method, you will get `#!python ValueError` exception at the runtime.


### {!core-concepts/_declare-parameters.md!}

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
    If you don't specify a return type, the decorator will return a `dict` object.
    But, your IDE will not be able to detect the type of the response, so it's recommended to specify the return type.
    Corresponding warning will be shown at the runtime.


### Class-based declaration

Class-based declaration is the most common way to declare clients. It's also the most flexible one.

Use the `BaseClient` class as a base class for your client and declare methods using the `declare` decorator.


#### Example

```.python title="my_client.py"
from declarativex import BaseClient, declare


class MyClient(BaseClient):
    base_url = "https://example.com"
    default_query_params = {"api_key": "123456"}
    default_headers = {"X-Trace": "<hash>"}

    @declare("GET", "/users/{user_id}", timeout=10)
    def get_user(self, user_id: int) -> dict:
        ...


my_client = MyClient()
```

!!! danger "Class-based declaration"
    If you're using class-based declaration, you must pass `self` as the first argument to the method.

    It will be used to get the `base_url`, `default_query_params` and `default_headers` values.


### Function-based declaration


Function-based declaration is a great alternative to class-based declaration. It's more concise and doesn't require
you to create a class. Commonly used for simple clients with one endpoint.

#### Example

```.python title="my_client.py"
from declarativex import declare


@declare(
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

!!! note "Function-based declaration"
    
    If you're using function-based declaration, you don't need to add `self` as first argument.
    The parameters of the decorator will be used to get the `base_url`, `default_query_params` and `default_headers` values.


## `#!python @rate_limiter` decorator

The `#!python @rate_limiter` decorator is used to limit the number of requests to the endpoint.

Use it to prevent your client from being banned by the server.

It supports both sync and async declarations.

### Syntax

```python
@rate_limiter(max_calls, interval)
@declare(...)
def method_name() -> dict:
    ...
```

### Parameters

- `max_calls` - maximum number of calls to the endpoint
- `interval` - interval between calls in seconds

!!! note "Rate limit"
    The rate limit is applied to the endpoint, not to the client.


### Example
```.python title="my_client.py"
from declarativex import declare, rate_limiter


@rate_limiter(max_calls=10, interval=60)
@declare("GET", "/users/{user_id}")
def get_user(user_id: int) -> dict:
    ...

```

