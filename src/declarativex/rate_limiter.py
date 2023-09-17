import asyncio
import time
from typing import Callable, Union, Awaitable

from .exceptions import RateLimitExceeded
from .utils import ReturnType, DeclaredDecorator


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


class rate_limiter(DeclaredDecorator):
    def __init__(self, max_calls: int, interval: float, reject: bool = False):
        self._bucket = Bucket(max_calls, interval)
        self._reject = reject
        self._loop = asyncio.get_event_loop()
        self._lock = asyncio.Lock()

    async def _decorate_async(
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

    def _decorate_sync(
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

    def refill(self):
        self._bucket.refill()

    def _decorate_class(self, cls: type) -> type:
        cls = super()._decorate_class(cls)
        setattr(cls, "refill", self.refill)
        return cls

    def __call__(
        self, func_or_class: Union[Callable[..., ReturnType], type]
    ) -> Union[Callable[..., ReturnType], type]:
        inner = super().__call__(func_or_class)
        setattr(inner, "refill", self.refill)
        return inner
