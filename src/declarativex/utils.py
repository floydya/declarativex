import abc
import asyncio
from functools import wraps
from typing import TypeVar, Callable, Union

from .exceptions import MisconfiguredException

ReturnType = TypeVar("ReturnType")
SUPPORTED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}
DECLARED_MARK = "_declarativex_declared"


class DeclaredDecorator(abc.ABC):
    @abc.abstractmethod
    async def _decorate_async(
        self, func: Callable, *args, **kwargs
    ):
        raise NotImplementedError

    @abc.abstractmethod
    def _decorate_sync(
        self, func: Callable, *args, **kwargs
    ):
        raise NotImplementedError

    def _decorate_class(self, cls: type) -> type:
        for attr_name, attr_value in cls.__dict__.items():
            if hasattr(attr_value, DECLARED_MARK):
                setattr(cls, attr_name, self(attr_value))
        setattr(cls, DECLARED_MARK, True)
        return cls

    @property
    def mark(self) -> str:
        return f"_{self.__class__.__name__}"

    def __call__(
        self, func_or_cls: Union[Callable[..., ReturnType], type]
    ) -> Union[Callable[..., ReturnType], type]:
        if hasattr(func_or_cls, self.mark):
            raise MisconfiguredException(
                f"Cannot decorate function with "
                f"@{self.__class__.__name__} twice"
            )

        if isinstance(func_or_cls, type):
            return self._decorate_class(func_or_cls)

        if asyncio.iscoroutinefunction(func_or_cls):

            @wraps(func_or_cls)
            async def inner(*args, **kwargs):
                return await self._decorate_async(func_or_cls, *args, **kwargs)

        else:

            @wraps(func_or_cls)
            def inner(*args, **kwargs):
                return self._decorate_sync(func_or_cls, *args, **kwargs)

        setattr(
            inner, DECLARED_MARK, getattr(func_or_cls, DECLARED_MARK, False)
        )
        setattr(inner, self.mark, True)
        return inner
