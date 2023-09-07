# Client declaration

DeclarativeX supports two ways of declaring clients: class-based and function-based. Both are equally powerful and
flexible, so it's up to you to decide which one to use.

## `declare` decorator

The `declare` decorator is the core of DeclarativeX. It's used to declare clients and their methods.

### Syntax

```python
@declare(method, path, base_url, timeout, default_headers, default_query_params)
def method_name():
    ...
```

### Parameters

This table outlines the arguments you can pass to the decorator, detailing their type, 
whether they're required or optional, and what each argument is for.

| Name                   | Type | Required            | Description                                                       |
|------------------------| ---- |---------------------|-------------------------------------------------------------------|
| `method`               | `str` | Yes                 | Specifies the HTTP method (e.g., GET, POST, PUT) you want to use. |
| `path`                 | `str` | Yes                 | Defines the API endpoint path you're hitting.                     |
| `base_url`             | `str` | No, see below...    | Sets the base URL for the request.                                |
| `timeout`              | `int` | No, default: `None` | The timeout to use.                                               |
| `default_headers`      | `dict` | No, default: `None` | The headers to use with every request.                            |
| `default_query_params` | `dict` | No, default: `None` | The parameters to use with every request.                         |

!!! warning "`(1) base_url`"
    This is necessary if the method is not part of a class that already specifies it.

### Priority of the parameters resolution

The priority of the parameters is as follows:

1. Pick parameter from the decorator.
2. Pick parameter from the class.
3. If both are specified, merge them.

!!! info "Priority"
    Decorator parameters have **higher** priority and will __overwrite__ the same values of class parameter


### Return Type

The `declare` decorator returns a `requests.Response` object. Type annotations are also supported.

You can use any of the custom dataclasses or Pydantic models to parse the response automatically.

!!! warning "-> dict"
    Don't place the return type `dict`. 

    The reason to not use `dict` is that it will be the same as the default return type, so it's redundant and will break IDE.

### Example

```.python title="my_client.py"
from declarativex import declare


@declare(
    method="GET", 
    path="/users/{user_id}", 
    base_url="https://example.com",
    timeout=10,
    default_query_params={"api_key": "123456"},
    default_headers={"X-Trace": "<hash>"}
)
def get_user(user_id: int):
    ...

```

## Class-based declaration

## Function-based declaration
