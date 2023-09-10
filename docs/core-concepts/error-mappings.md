# Error mapping

## Overview

Error mapping is a way to map errors from one type to another. 
This is useful when you want to parse errors from an external API to your own schema.

## Example

```python title="my_client.py" hl_lines="6 7 13 22 23 24"
from declarativex import declare, Json
from declarativex.exceptions import HTTPException
from pydantic import BaseModel


class BadRequestSchema(BaseModel):
    email: str


@declare(
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
