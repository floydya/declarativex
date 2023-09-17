---
title: Error Mappings - Core Concepts in DeclarativeX
description: Discover how to map errors in DeclarativeX. Get insights into customizing error responses for better exception handling.
---

# Error mapping

## Overview

Error mapping is a way to map errors from one type to another. 
This is useful when you want to parse errors from an external API to your own schema.

## Default behavior

By default, if the server returns an error, the client will raise an `HTTPException` with the following attributes:

- `status_code` - HTTP status code of the response, integer.
- `response` - `httpx.Response` object.
- `raw_request` - [RawRequest](../api/models.md#class-rawrequest) object.


## Mapping errors

You can map errors to your own schema by using the `error_mappings` argument of the `@http` decorator. 

You can also use `BaseClient` class to set error mappings for all endpoints.

!!! note
    If you set error mappings for a specific endpoint, it will override the error mappings set in the `BaseClient` class.


### Example

```python title="my_client.py" hl_lines="6 7 13 22 23 24"
from declarativex import http, Json
from declarativex.exceptions import HTTPException
from pydantic import BaseModel


class BadRequestSchema(BaseModel):
    email: str


@http(
    "POST", 
    "/users/", 
    error_mappings={400: BadRequestSchema}
)
def create_user(user_data: dict = Json(...)) -> dict:
    """ Endpoint is raising 400 error. """
    ...


try:
    create_user(user_data={"email": "john@example.com"})
except HTTPException as e:
    print(e.status_code)  # 400
    print(e.response)  # BadRequestSchema(email='User with this email already exists.')
```

!!! success
    Now, if the server returns a `400` error, it will be parsed to `BadRequestSchema` automatically.
