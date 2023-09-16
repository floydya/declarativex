# Middlewares

## Overview

The Middleware feature allows you to inject custom logic into the request/response cycle of an HTTP client library. Middlewares can be both synchronous and asynchronous, providing a versatile way to modify outgoing requests or handle incoming responses.

## Usage

To create your middleware, extend the Middleware class and implement the __call__ method.

### Synchronous Middleware

Here's an example of a synchronous middleware that logs information before and after the call_next invocation.

```python
import logging

from declarativex import Middleware


class FooMiddleware(Middleware):
    def __call__(self, *, request, call_next):
        logging.info("pre FooMiddleware")
        response = call_next(request)
        logging.info("post FooMiddleware")
        return response
```

### Asynchronous Middleware

For async operations, you can define the __call__ method as asynchronous.

```python
import logging

from declarativex import Middleware


class FooMiddleware(Middleware):
    async def __call__(self, *, request, call_next):
        logging.info("pre FooMiddleware")
        response = await call_next(request)
        logging.info("post FooMiddleware")
        return response
```

## Signature checking

The Middleware class uses a metaclass to check the signature of the __call__ method. 
This ensures that the middleware is implemented correctly and that the executor can invoke it properly.

### Inheriting from `Middleware`

To create your own middleware, you simply inherit from the Middleware class and implement the __call__ method. 
The Signature metaclass will automatically check the __call__ method's signature at the time of class definition.

Here's how you could inherit from the Middleware class:

```python
class CustomMiddleware(Middleware):
    def __call__(self, *, request: RawRequest, call_next: Callable[[RawRequest], ReturnType]) -> ReturnType:
        # Your custom logic here
```

## Synchronous and Asynchronous Middleware Interactions

### Sync in Async and Async in Sync

While both synchronous and asynchronous middlewares can be created, it's important to note that they can't be mixed within the same HTTP function. Attempting to do so will result in a runtime exception. Here's how this validation works in practice:

#### Sync Middleware in Async Function

If you try to use a synchronous middleware within an asynchronous function, you'll encounter a [`MisconfiguredException`](../api/exceptions.md#class-misconfiguredexception).

```python hl_lines="7 22 24"
import pytest

from declarativex import http, MisconfiguredException, Middleware


class FooMiddleware(Middleware):
    def __call__(self, *, request, call_next):
        ...


class AsyncBarMiddleware(Middleware):
    async def __call__(self, *, request, call_next):
        ...


@pytest.mark.asyncio
async def test_sync_async_middleware():
    @http(
        "GET", 
        "api/users", 
        base_url="https://example.com", 
        middlewares=[FooMiddleware(), AsyncBarMiddleware()]
    )
    async def get_users():
        pass

    with pytest.raises(MisconfiguredException) as exc:
        await get_users()

    assert str(exc.value) == "Cannot use sync middleware with async function"
```

#### Async Middleware in Sync Function

Likewise, using an asynchronous middleware within a synchronous function will also trigger a [`MisconfiguredException`](../api/exceptions.md#class-misconfiguredexception).

```python hl_lines="12 21 23"
import pytest

from declarativex import http, MisconfiguredException, Middleware


class FooMiddleware(Middleware):
    def __call__(self, *, request, call_next):
        ...


class AsyncBarMiddleware(Middleware):
    async def __call__(self, *, request, call_next):
        ...


def test_sync_async_middleware():
    @http(
        "GET", 
        "api/users", 
        base_url="https://example.com", 
        middlewares=[FooMiddleware(), AsyncBarMiddleware()]
    )
    def get_users():
        pass

    with pytest.raises(MisconfiguredException) as exc:
        get_users()

    assert str(exc.value) == (
        "Cannot use sync middleware(FooMiddleware) with async function"
    )
```

### How the Validation Works

The middleware validation occurs at the runtime. It checks the _async attribute, which is set by the Signature meta-class. The _async attribute specifies whether the __call__ method in the middleware is asynchronous or not. The executor then uses this attribute to determine if a middleware is valid for a given function type.

This ensures that the middleware type matches the function type (async-to-async or sync-to-sync), maintaining the integrity and expected behavior of the HTTP client library.

By strictly prohibiting the mixing of sync and async, the library ensures that developers avoid unexpected behavior or tricky debugging scenarios. This makes for a more robust and predictable development experience.

## Examples

### Simple in-memory cache for GET requests

Here's an example of a simple in-memory cache for GET requests. It uses a dictionary to store the responses and returns the cached response if the request URL is already in the cache.

```python
from declarativex import Middleware


class CacheMiddleware(Middleware):
    cache = {}

    def __call__(self, *, request, call_next):
        if request.method != "GET":
            return call_next(request)
        url = request.url()
        if url in self.cache:
            return self.cache.get(url)
        response = call_next(request)
        self.cache[url] = response
        return response
```
