---
title: GraphQL - Core Concepts in DeclarativeX
description: Explore the GraphQL client in DeclarativeX. Learn how to set up and customize your GraphQL clients for various web services.
---

# `@gql` decorator

The `@gql` decorator allows you to declare GraphQL clients, either through class-based or 
function-based declarations, much like how the [`@http`](./http-declaration.md) decorator works. 
The primary difference is that you'll be defining a GraphQL query or 
mutation rather than an HTTP method and path.


## Syntax

=== "Sync"
    ```python
    @gql(query, *, base_url, timeout, default_headers, default_query_params, middlewares)
    def method_name() -> dict:
        ...
    ```

=== "Async"
    ```python
    @gql(query, *, base_url, timeout, default_headers, default_query_params, middlewares)
    async def method_name() -> dict:
        ...
    ```

### Arguments Table

The arguments for `@gql` are quite similar to those for [`@http`](./http-declaration.md#declare-parameters). 
Instead of specifying an HTTP method and path, you specify a GraphQL query.

| Argument | Type | Description |
| -------- | ---- | ----------- |
| `query` | `str` | The GraphQL query to be executed. |

!!! note "Keyword-only arguments"
    All arguments after `query` are keyword-only arguments, so you must specify them by name.

### Priority of the parameters resolution

The priority follows the same rules as in the [`@http` decorator](./http-declaration.md#priority-of-the-parameters-resolution).
