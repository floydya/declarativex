---
title: Auth - Core Concepts in DeclarativeX
description: Dive into authentication in DeclarativeX. Learn how to add authentication to your HTTP clients.
---

# Authentication

## Overview

The Authentication feature allows you to simplify the process of adding authentication to your HTTP clients.

## Authentication Types

DeclarativeX supports the following authentication types:

|     Class name      |  Location  | Description                                                                                                    |
|:-------------------:|:----------:|----------------------------------------------------------------------------------------------------------------|
|     `BasicAuth`     |   Header   | Provide username and password, <br>it will add base64-encoded `username:password` into `Authorization` header. |
|    `BearerAuth`     |   Header   | Provide a token and it will add `Authorization: Bearer {token}` to headers.                                    |
|    `HeaderAuth`     |   Header   | Provide header name and token = `{header_name}: {token}`.                                                      |
|  `QueryParamsAuth`  |   Query    | Provide a key and value, it will add it to query params: `{url}?{key}={value}`                                 |


### BasicAuth

```python
from declarativex import BasicAuth

auth = BasicAuth(username="my_username", password="my_password")
```

### BearerAuth

```python
from declarativex import BearerAuth

auth = BearerAuth("my_token")
```

### HeaderAuth

```python
from declarativex import HeaderAuth

auth = HeaderAuth(header_name="X-My-Header", value="my_token")
```

### QueryParamsAuth

```python
from declarativex import QueryParamsAuth

auth = QueryParamsAuth(key="key", value="my_token")
```

## Usage

### Class-based declaration

```python
from declarativex import http, BaseClient, BearerAuth


class MyClient(BaseClient):
    base_url = ...
    auth = BearerAuth("my_token")

    @http("GET", "/users")
    def get_users(self) -> dict:
        ...

```

### Function-based declaration

```python
from declarativex import http, BearerAuth


@http("GET", "/users", auth=BearerAuth("my_token"))
def get_users() -> dict:
    ...

```

!!! note
  If auth declared in both class and function, the function auth will be used because it has more prioritized parameters.
