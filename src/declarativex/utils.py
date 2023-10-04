import abc
import asyncio
from functools import wraps
from typing import TypeVar, Callable, Union, Any

from .exceptions import MisconfiguredException
from .warnings import warn_support_decorator_ignored

ReturnType = TypeVar("ReturnType")
SUPPORTED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}
DECLARED_MARK = "_declarativex_declared"


class Decorator(abc.ABC):
    MARK_TEMPLATE = "_{cls_name}"

    @abc.abstractmethod
    async def _decorate_async(self, func: Callable, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def _decorate_sync(self, func: Callable, *args, **kwargs):
        raise NotImplementedError

    def _check_already_decorated(self, obj: Any):
        if hasattr(obj, self.mark):
            raise MisconfiguredException(
                f"Cannot decorate function with "
                f"@{self.__class__.__name__} twice"
            )

    @classmethod
    def get_all_subclasses(cls):
        subclasses = cls.__subclasses__()
        for sub in subclasses:
            if hasattr(sub, "get_all_subclasses"):
                subclasses.extend(sub.get_all_subclasses())
        return subclasses

    @classmethod
    def _subclasses_marks(cls):
        return {
            cls.MARK_TEMPLATE.format(cls_name=sub.__name__)
            for sub in cls.get_all_subclasses()
        }

    @property
    def mark(self) -> str:
        return self.MARK_TEMPLATE.format(cls_name=self.__class__.__name__)

    def __call__(
        self, func: Callable[..., ReturnType]
    ) -> Callable[..., ReturnType]:
        self._check_already_decorated(func)

        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def inner(*args, **kwargs):
                return await self._decorate_async(func, *args, **kwargs)

        else:

            @wraps(func)
            def inner(*args, **kwargs):
                return self._decorate_sync(func, *args, **kwargs)

        setattr(inner, self.mark, True)
        return inner


class SupportDecorator(Decorator, abc.ABC):
    @staticmethod
    def _check_declared(obj: Any):
        return any(
            hasattr(obj, mark) for mark in Decorator._subclasses_marks()
        )

    def _decorate_class(self, cls: type) -> type:
        self._check_already_decorated(cls)
        for attr_name, attr_value in cls.__dict__.items():
            if self._check_declared(attr_value):
                setattr(cls, attr_name, self(attr_value))
        return cls

    def __call__(
        self, func_or_cls: Union[Callable[..., ReturnType], type]
    ) -> Union[Callable[..., ReturnType], type]:
        if isinstance(func_or_cls, type):
            return self._decorate_class(func_or_cls)
        if not self._check_declared(func_or_cls):
            warn_support_decorator_ignored(self.__class__.__name__)
            return func_or_cls
        return super().__call__(func_or_cls)
