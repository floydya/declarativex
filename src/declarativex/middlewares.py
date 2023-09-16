import abc
import asyncio
import inspect
from typing import (
    Callable,
    TYPE_CHECKING,
    TypeVar,
)

if TYPE_CHECKING:
    from .models import RawRequest

ReturnType = TypeVar("ReturnType")


class Signature(abc.ABCMeta):
    expected_signature = {
        "self",
        "request",
        "call_next",
    }

    def __new__(mcs, name, bases, namespace, /, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        signature = inspect.signature(namespace.get("__call__"))
        parameters_left = dict(signature.parameters)
        for parameter_name in mcs.expected_signature:
            if parameter_name not in parameters_left:
                raise TypeError(
                    f"Expected parameter '{parameter_name}' "
                    f"in {cls.__name__}.__call__"
                )
            del parameters_left[parameter_name]
        if parameters_left:
            raise TypeError(
                f"Unexpected parameters {list(parameters_left.keys())} "
                f"in {cls.__name__}.__call__"
            )
        setattr(cls, "_async", asyncio.iscoroutinefunction(cls.__call__))
        return cls


class Middleware(abc.ABC, metaclass=Signature):
    @abc.abstractmethod
    def __call__(
        self,
        *,
        request: "RawRequest",
        call_next: Callable[["RawRequest"], ReturnType],
    ) -> ReturnType:
        raise NotImplementedError
