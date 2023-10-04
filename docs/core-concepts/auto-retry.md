---
title: Auto Retry - Core Concepts in DeclarativeX
description: Understand the auto-retry mechanism in DeclarativeX. Learn how to implement retries in your HTTP clients for better fault tolerance.
---

# Auto retry

## What is auto retry?

Auto retry is a feature that allows you to automatically retry a failed HTTP request. This is useful when you want to retry a request that failed due to a network error or a timeout.

## How does it work?

When you make a request, the request is sent to the server. If the server responds with an error, the request is retried. If the server responds with a success, the request is not retried.

## How do I use it?

To use auto retry, you need to decorate your endpoint method with `@retry`.

It takes four arguments:

- `max_retries`: The maximum number of times to retry the request.
- `backoff_factor`: The backoff factor to use when retrying the request.
- `exceptions`: The list of status codes to retry.
- `delay`: The delay between retries.


```python
from declarativex import retry, http, TimeoutException


@retry(max_retries=3, backoff_factor=0.5, exceptions=(TimeoutException,), delay=0.5)
@http("GET", "/status/500", base_url="https://httpbin.org", timeout=0.1)
def get():
    pass
```
