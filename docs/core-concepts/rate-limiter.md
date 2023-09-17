---
title: Rate Limiter - Core Concepts in DeclarativeX
description: Understand rate limiting in DeclarativeX. Learn how to use rate limiter to manage API requests efficiently.
---

# Rate limiter

There is a way to not get banned by the external API you're using. It's called rate limiting.

## Algorithm

So, the Token Bucket algorithm is pretty rad. It works like this:

1. You start with a bucket that can hold a set number of tokens. 
2. Tokens are added at a fixed rate up to the bucket's max capacity. 
3. When a request comes in, it takes a token from the bucket to proceed. 
4. If the bucket's empty, the request has to wait. 

Simple, right?

### Comparison with other algorithms

#### Fixed Window Algorithm

The fixed window algorithm is the simplest rate limiting algorithm. It works like this:

1. You start with a counter set to 0.
2. When a request comes in, you increment the counter.
3. After a fixed amount of time, the counter is reset to 0.
4. If the counter is greater than the max number of requests, the request is rejected.
5. Otherwise, the request is allowed.
6. Repeat.

!!! success "Simple to implement."

!!! danger "Not very accurate, can cause rate spikes at the window boundaries."

#### Sliding Window Algorithm

The sliding window algorithm is a bit more complex. It works like this:

1. You start with a counter set to 0.
2. When a request comes in, you increment the counter.
3. After a fixed amount of time, you decrement the counter.
4. If the counter is greater than the max number of requests, the request is rejected.
5. Otherwise, the request is allowed.
6. Repeat.

It is like mix of the fixed window and token bucket algorithms.

!!! success "Smoothens out the spikes in the fixed window algorithm."
!!! danger "More complex and can be resource-intensive."

#### Leaky Bucket Algorithm

The opposite of the token bucket algorithm is the leaky bucket algorithm. It works like this:

All incoming requests go into a bucket and leak out at a constant rate.

1. You start with a bucket that can hold a set number of tokens.
2. Tokens are added at a fixed rate up to the bucket's max capacity.
3. When a request comes in, it takes a token from the bucket to proceed.
4. If the bucket's empty, the request has to wait.
5. If the bucket's full, the request is rejected.
6. Repeat.

!!! success "Easy to predict request timing."
!!! danger "Can drop requests if the bucket is full, causing some loss of service."

#### Why Token Bucket?

The token bucket algorithm is a good choice for rate limiting because it's simple to implement and easy to understand.

It also has a nice property that the rate of requests is constant over time, which makes it easy to predict when requests will be allowed.

## `#!python @rate_limiter` decorator

The `#!python @rate_limiter` decorator is used to limit the number of requests to the endpoint.

Use it to prevent your client from being banned by the server.

It supports both sync and async declarations.

## Syntax

=== "Per endpoint"
    ```python hl_lines="3"
    from declarativex import http, rate_limiter

    @rate_limiter(max_calls: int, interval: float, reject: bool)
    @http(...)
    def method_name() -> dict:
        ...
    ```

    !!! info
        It will be applied to the decorated endpoint. The bucket will be bounded to it. Only this function will consume bucket tokens.


=== "Per client"
    ```python hl_lines="4"
    from declarativex import http, rate_limiter, BaseClient


    @rate_limiter(max_calls, interval)
    class MyClient(BaseClient):
        base_url = "https://api.example.com"

        @http("GET", "/users")
        def get_users(self) -> dict:
            ...

        @http("GET", "/users/{user_id}")
        def get_user(self, user_id: int) -> dict:
            ...
    ```

    !!! info
        It will be applied to all endpoints of the client. The bucket will be shared. Every endpoint will consume tokens from the same bucket.

## Parameters

- `max_calls` - maximum number of calls to the endpoint
- `interval` - interval between calls in seconds
- `reject` - whether to reject the request or wait for the next interval. Defaults to `False`, if `True` - raises [`RateLimitExceeded`](../api/exceptions.md#class-ratelimitexceeded) exception.
