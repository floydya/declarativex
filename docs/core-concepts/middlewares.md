# Middlewares

## What is a Middleware?

A middleware is a class that can modify request and response.
It is used to add some additional functionality to the client.
For example, you can add authentication to the client using a middleware.

## Middleware types

There are two types of middlewares:

- `AsyncMiddleware`
- `SyncMiddleware`

You can use AsyncMiddleware only with async methods and SyncMiddleware only with sync methods.

!!! info

    The [MisconfiguredException](./exceptions.md#misconfiguredexception) will be raised if you use the wrong type of middleware.

Both of base classes implements `process_request` and `process_response` methods.
!!! example

    === "AsyncMiddleware"
    
        ```python title="middleware.py" hl_lines="6 7 10 11"
        from declarativex import AsyncMiddleware
        
        
        class MyAsyncMiddleware(AsyncMiddleware):
            async def process_request(self, request):
                # Modify request here
                return request
        
            async def process_response(self, response):
                # Modify response here
                return response
        ```

    === "SyncMiddleware"
    
        ```python title="middleware.py" hl_lines="6 7 10 11"
        from declarativex import Middleware
        
        
        class MyMiddleware(Middleware):
            def process_request(self, request):
                # Modify request here
                return request
        
            def process_response(self, response):
                # Modify response here
                return response
        ```

## Declaration

You can set up your middlewares in two ways:

- Using `middlewares` parameter in the `#!python BaseClient` constructor.
- Using `middlewares` parameter in the `#!python @declare`.

If both of them are specified, they will be merged for specific endpoint.
