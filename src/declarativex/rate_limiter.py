import asyncio
import time
from functools import wraps
from typing import TypeVar, Callable

ReturnType = TypeVar("ReturnType")


def rate_limiter(
    max_calls: float, interval: float
) -> Callable[..., ReturnType]:
    """
    Rate-limits the decorated function locally, for one process.
    Using Token Bucket algorithm.
        - max_calls: maximum number of calls of function in interval
        - interval: interval in [s]
    """

    token_fill_rate: float = max_calls / interval

    def decorate(func):
        last_time_token_added = time.perf_counter()
        token_bucket = max_calls

        @wraps(func)
        async def async_rate_limited_function(*args, **kwargs):
            nonlocal last_time_token_added
            nonlocal token_bucket
            try:
                elapsed = time.perf_counter() - last_time_token_added
                # refill token_bucket to a maximum of max_calls
                token_bucket = min(
                    token_bucket + elapsed * token_fill_rate, max_calls
                )
                last_time_token_added = time.perf_counter()

                # check if we have to wait for a function call
                # (min 1 token in order to make a call)
                if token_bucket < 1.0:
                    left_to_wait = (1 - token_bucket) / token_fill_rate
                    await asyncio.sleep(left_to_wait)

                return await func(*args, **kwargs)
            finally:
                # for every call we can consume one token,
                # if the bucket is empty, we have to wait
                token_bucket -= 1.0

        @wraps(func)
        def sync_rate_limited_function(*args, **kwargs):
            nonlocal last_time_token_added
            nonlocal token_bucket
            try:
                elapsed = time.perf_counter() - last_time_token_added
                # refill token_bucket to a maximum of max_calls
                token_bucket = min(
                    token_bucket + elapsed * token_fill_rate, max_calls
                )
                last_time_token_added = time.perf_counter()

                # check if we have to wait for a function call
                # (min 1 token in order to make a call)
                if token_bucket < 1.0:
                    left_to_wait = (1 - token_bucket) / token_fill_rate
                    time.sleep(left_to_wait)

                return func(*args, **kwargs)
            finally:
                # for every call we can consume one token,
                # if the bucket is empty, we have to wait
                token_bucket -= 1.0

        return (
            async_rate_limited_function
            if asyncio.iscoroutinefunction(func)
            else sync_rate_limited_function
        )

    return decorate
