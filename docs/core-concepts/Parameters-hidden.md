# Dependencies 

## Introduction

Parameters are a powerful feature of DeclarativeX that let you customize your HTTP requests. 

They're designed to make your life easier, letting you focus on what really matters — your application logic.

## Types of Dependencies

DeclarativeX supports the following types:

- [Path parameter](#path-parameter)
- [Query parameter](#query-parameter)
- [BodyField parameter](#body-field-parameter)
- [Json parameter](#json-parameter)


!!! note
    The order of parameters in the function doesn't matter.


## How it works under the hood?

DeclarativeX uses [inspect.signature](https://docs.python.org/3/library/inspect.html#inspect.signature) to get 
the function's signature and then parses it to get the list of parameters.

Then it iterates over the list of parameters and:

- If it is a [Path parameter](#path-parameter) declaration, it replaces the corresponding path parameter in the URL.
- If it is a [Query parameter](#query-parameter) declaration, it adds the corresponding query parameter to the URL.
- If it is a [BodyField parameter](#body-field-parameter) declaration, it `adds` the corresponding field to the request body.
- If it is a [Json parameter](#json-parameter) declaration, it `sets` the corresponding field to the request body.


### Default behavior

- If the parameter has no declaration in the function, it will check if the parameter is in `path` variables. 
    - If it is, it will replace the corresponding `path` parameter in the URL automatically.
    - If it's not, it will add the corresponding `query` parameter to the URL automatically.
- If the parameter has a declaration in the function, it will use the declaration instead of the default behavior.


### Default kwargs

Each of the parameters provides the following default kwargs.

- `default`

:   The default value to use if there is no data passed to function, if not provided the field is required.

- `field_name`

:   The name of the field to use, if nothing is passed, it will use the name of the parameter.

## Path parameter

Path parameters are used to replace the corresponding path parameter in the URL.

!!! note
    Path parameter is not required, it can be automatically calculated using path string.

    Also, you can manually define a declaration using `#!python Path(...)`.

### Examples


=== "Automatic declaration"
    ```.python title="my_client.py" hl_lines="6"
    from declarativex import declare
    
    
    @declare("GET", "/users/{user_id}")
    def get_user(
        user_id: int
    ) -> dict:
        ...
    ```

=== "Manual declaration"
    ```.python title="my_client.py" hl_lines="6"
    from declarativex import declare, Path
    
    
    @declare("GET", "/users/{user_id}")
    def get_user(
        user_id: int = Path(...)
    ) -> dict:
        ...
    ```

!!! note
    Both automatic and manual declarations are interchangeable. You can use any of them.


## Query parameter

Query parameters are used to add the corresponding query parameter to the URL.

!!! note
    Query parameter is not required, it can be automatically calculated using function signature.

    Also, you can manually define a declaration using `#!python Query(...)`.

### Examples

<div class="annotate" markdown>

=== "Automatic declaration"
    ```.python title="my_client.py" hl_lines="7 8"
    from declarativex import declare
    
    
    @declare("GET", "/users/{user_id}")
    def get_users(
        user_id: int,  # (1)
        page: int,  # (2)
        limit: int,  # (3)
    ) -> dict:
        ...
    ```

=== "Manual declaration"
    ```.python title="my_client.py" hl_lines="7 8"
    from declarativex import declare, Query

    
    @declare("GET", "/users/{user_id}")
    def get_users(
        user_id: int,  # (1)
        page: int = Query(...),  # (4)
        limit: int = Query(...),  # (5)
    ) -> dict:
        ...
    ```

</div>

1.  It will find `user_id` in `/users/{user_id}` string and declare it as `Path` **automatically**.
2.  Since there is no `page` in `/users/{user_id}` string it will be declared as `Query`.
3.  Since there is no `limit` in `/users/{user_id}` string it will be declared as `Query`.
4.  We can manually declare `page` as `Query` parameter.
5.  We can manually declare `limit` as `Query` parameter.


## BodyField parameter

BodyField parameters are used to add the corresponding field to the request body.

It is used to 

!!! note
    If you need to declare a BodyField parameter, it should be manually declared using `#!python BodyField(...)`.


