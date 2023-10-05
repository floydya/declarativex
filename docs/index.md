---
title: DeclarativeX Documentation
description: Welcome to DeclarativeX documentation. Get started with this Python library for building robust, declarative HTTP clients.
---

# Welcome to DeclarativeX 🚀

## Introduction

Hey there! Welcome to the official documentation of DeclarativeX. If you're tired of writing boilerplate code for HTTP
clients and want a more declarative approach, you're in the right place. DeclarativeX is designed to make your life
easier, letting you focus on what really matters—your application logic.

## Installation

Getting started with DeclarativeX is a breeze. Just run the following command:

```bash
pip install declarativex
```

And boom! You're good to go.

## Available extras

DeclarativeX comes with a few extras that you can install separately. Here's a list of available extras:

- `http2` - HTTP/2 support
- `graphql` - GraphQL support
- `brotli` - Brotli compression support

To install an extra, just add it to the end of the command:

=== "All"
    ```bash
    pip install declarativex[http2,graphql,brotli]
    ```

=== "Only one"
    ```bash
    pip install declarativex[http2]
    ```

## Quick Start Guide

Ready to dive in? Here's a quick example to get you started:

=== "Sync"
    ```{.python title="my_client.py"}
    from declarativex import BaseClient, http
    
    
    @http("GET", "/users/{user_id}", "https://example.com")
    def get_user(user_id: int) -> dict:
        ...
    
    
    response = get_user(user_id=1)
    print(response)
    ```

=== "Async"
    ```{.python title="my_client.py"}
    import asyncio
    
    from declarativex import BaseClient, http
    
    
    @http("GET", "/users/{user_id}", "https://example.com")
    async def get_user(user_id: int) -> dict:
        ...
    
    
    response = asyncio.run(get_user(user_id=1))
    print(response)
    ```

!!! success "You should see the following output:"
    ```
    {
      "id": 1,
      "name": "John Doe"
    }
    ```

!!! tip "Async"
    DeclarativeX supports both synchronous and asynchronous HTTP requests. Just define your function as `async` and
    you're good to go.


See? No fuss, just clean and straightforward code.

## Why DeclarativeX?

- **Less Boilerplate**: No more repetitive code for HTTP methods.
- **Type-Safe**: Built with type annotations for better code quality.
- **Flexible**: Easily extendable to fit your specific needs.

## What's Next?

Feel free to explore the documentation to get a deeper understanding of DeclarativeX. Whether you're looking to understand the core concepts, decorators, or how to set up dependencies, we've got you covered.

- [BaseClient](core-concepts/base-client.md)
- [HTTP Declaration](core-concepts/http-declaration.md)
- [Dependencies](core-concepts/dependencies.md)
- [Middlewares](core-concepts/middlewares.md)

## Contributing

Love DeclarativeX and want to contribute? Awesome! Check out our [Contribution Guidelines](contributing.md).

