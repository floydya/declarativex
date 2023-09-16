import asyncio
import time
from functools import wraps
from typing import TypeVar, Callable, Union, Awaitable

from .exceptions import RateLimitExceeded

ReturnType = TypeVar("ReturnType")


class Bucket:
    token_fill_rate: float
    last_time_token_added: float
    token_bucket: float

    def __init__(self, max_calls: float, interval: float):
        self._max_calls = max_calls
        self._interval = interval

        self.token_fill_rate = max_calls / interval
        self.last_time_token_added = 0.0
        self.token_bucket = max_calls

    @property
    def max_calls(self):
        return self._max_calls

    def refill(self):
        self.token_bucket = self._max_calls
        self.last_time_token_added = 0.0


class rate_limiter:
    def __init__(self, max_calls: int, interval: float, reject: bool = False):
        self._bucket = Bucket(max_calls, interval)
        self._reject = reject
        self._loop = asyncio.get_event_loop()
        self._lock = asyncio.Lock()

    async def decorate_async(
        self, func: Callable[..., Awaitable[ReturnType]], *args, **kwargs
    ) -> ReturnType:
        async with self._lock:
            try:
                elapsed = (
                    self._loop.time()
                    - self._bucket.last_time_token_added
                )
                self._bucket.token_bucket = min(
                    self._bucket.token_bucket
                    + elapsed * self._bucket.token_fill_rate,
                    self._bucket.max_calls,
                )
                self._bucket.last_time_token_added = (
                    self._loop.time()
                )

                # check if we have to wait for a function call
                # (min 1 token in order to make a call)
                if self._bucket.token_bucket < 1.0:
                    if self._reject:
                        raise RateLimitExceeded()
                    left_to_wait = (
                        1 - self._bucket.token_bucket
                    ) / self._bucket.token_fill_rate
                    await asyncio.sleep(left_to_wait)

                return await func(*args, **kwargs)
            finally:
                # for every call we can consume one token,
                # if the bucket is empty, we have to wait
                self._bucket.token_bucket -= 1.0

    def decorate_sync(
        self, func: Callable[..., ReturnType], *args, **kwargs
    ) -> ReturnType:
        try:
            elapsed = time.perf_counter() - self._bucket.last_time_token_added
            self._bucket.token_bucket = min(
                self._bucket.token_bucket
                + elapsed * self._bucket.token_fill_rate,
                self._bucket.max_calls,
            )
            self._bucket.last_time_token_added = time.perf_counter()

            # check if we have to wait for a function call
            # (min 1 token in order to make a call)
            if self._bucket.token_bucket < 1.0:
                if self._reject:
                    raise RateLimitExceeded()
                left_to_wait = (
                    1 - self._bucket.token_bucket
                ) / self._bucket.token_fill_rate
                time.sleep(left_to_wait)

            return func(*args, **kwargs)
        finally:
            # for every call we can consume one token,
            # if the bucket is empty, we have to wait
            self._bucket.token_bucket -= 1.0

    def decorate_class(self, cls: type) -> type:
        for attr_name, attr_value in cls.__dict__.items():
            if hasattr(attr_value, "_declarativex"):
                setattr(cls, attr_name, self(attr_value))
        setattr(cls, "_rate_limiter_bucket", self._bucket)
        return cls

    def __call__(
        self, func_or_class: Union[Callable[..., ReturnType], type]
    ) -> Union[Callable[..., ReturnType], type]:
        if isinstance(func_or_class, type):
            return self.decorate_class(func_or_class)

        if asyncio.iscoroutinefunction(func_or_class):

            @wraps(func_or_class)
            async def inner(*args, **kwargs):
                return await self.decorate_async(
                    func_or_class, *args, **kwargs
                )

        else:

            @wraps(func_or_class)
            def inner(*args, **kwargs):
                return self.decorate_sync(func_or_class, *args, **kwargs)

        setattr(inner, "_rate_limiter_bucket", self._bucket)
        return inner
