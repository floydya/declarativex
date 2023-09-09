import asyncio
from abc import ABC, abstractmethod
from typing import Callable, Generic, TypeVar, Coroutine

import httpx

from .exceptions import MisconfiguredException

ReturnType = TypeVar("ReturnType")


class Middleware(Generic[ReturnType], ABC):
    func: Callable[..., ReturnType]

    def set_func(self, func: Callable[..., ReturnType]):
        if asyncio.iscoroutinefunction(func):
            raise MisconfiguredException(
                "Middleware cannot be used with async functions, "
                "use AsyncMiddleware instead."
            )
        self.func = func

    @abstractmethod
    def modify_request(self, request: httpx.Request) -> httpx.Request:
        return request  # pragma: no cover

    @abstractmethod
    def modify_response(self, response: ReturnType) -> ReturnType:
        return response  # pragma: no cover


class AsyncMiddleware(Generic[ReturnType], ABC):
    func: Callable[..., Coroutine]

    def set_func(self, func: Callable[..., Coroutine]):
        if not asyncio.iscoroutinefunction(func):
            raise MisconfiguredException(
                "AsyncMiddleware cannot be used with sync functions, "
                "use Middleware instead."
            )
        self.func = func

    @abstractmethod
    async def modify_request(self, request: httpx.Request) -> httpx.Request:
        return request  # pragma: no cover

    @abstractmethod
    async def modify_response(self, response: ReturnType) -> ReturnType:
        return response  # pragma: no cover
