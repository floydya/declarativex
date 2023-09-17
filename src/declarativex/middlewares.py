import abc
import asyncio
import inspect
from typing import (
    Callable,
    TYPE_CHECKING,
)

from .utils import ReturnType

if TYPE_CHECKING:
    from .models import RawRequest


class Signature(abc.ABCMeta):
    expected_signature = {
        "self",
        "request",
        "call_next",
    }

    def __new__(mcs, name, bases, namespace, /, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        # Check if __call__ has the expected signature
        signature = inspect.signature(namespace.get("__call__"))
        parameters_left = dict(signature.parameters)
        for parameter_name in mcs.expected_signature:
            if parameter_name not in parameters_left:
                # The parameter is missing, raise an error
                raise TypeError(
                    f"Expected parameter '{parameter_name}' "
                    f"in {cls.__name__}.__call__"
                )
            # Remove the parameter from the list of expected parameters
            del parameters_left[parameter_name]
        if parameters_left:
            # There are unexpected parameters, raise an error
            raise TypeError(
                f"Unexpected parameters {list(parameters_left.keys())} "
                f"in {cls.__name__}.__call__"
            )
        # Check if __call__ is a coroutine function
        setattr(cls, "_async", asyncio.iscoroutinefunction(cls.__call__))
        return cls


class Middleware(abc.ABC, metaclass=Signature):
    """
    Base class for middleware. Middleware are classes that can be used to
    modify the request before it is passed to the next middleware or the
    endpoint.
    """
    @abc.abstractmethod
    def __call__(
        self,
        *,
        request: "RawRequest",
        call_next: Callable[["RawRequest"], ReturnType],
    ) -> ReturnType:
        raise NotImplementedError
