import asyncio
import time
from typing import Callable

from .utils import DeclaredDecorator


class retry(DeclaredDecorator):
    def __init__(
        self,
        max_retries: int,
        exceptions: tuple,
        delay: float = 0.0,
        backoff_factor: float = 1.0,
    ):
        self._max_retries = max_retries
        self._delay = delay
        self._backoff_factor = backoff_factor
        self._exceptions = exceptions

    async def _decorate_async(
        self, func: Callable, *args, **kwargs
    ):
        retries = 0
        current_delay = self._delay
        while retries <= self._max_retries:
            try:
                return await func(*args, **kwargs)
            except self._exceptions as e:
                retries += 1
                if retries > self._max_retries:
                    raise e
                await asyncio.sleep(current_delay)
                current_delay *= self._backoff_factor
        return None  # pragma: no cover

    def _decorate_sync(
        self, func: Callable, *args, **kwargs
    ):
        retries = 0
        current_delay = self._delay
        while retries <= self._max_retries:
            try:
                return func(*args, **kwargs)
            except self._exceptions as e:
                retries += 1
                if retries > self._max_retries:
                    raise e
                time.sleep(current_delay)
                current_delay *= self._backoff_factor
        return None  # pragma: no cover
