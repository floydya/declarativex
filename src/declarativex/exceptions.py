from collections.abc import Iterable
from typing import Type, Sequence, Union

import httpx


class DeclarativeException(Exception):
    pass


class MisconfiguredException(DeclarativeException):
    pass


class DependencyValidationError(DeclarativeException):
    def __init__(
        self, expected_type: Union[Type, Sequence[Type]], received_type: Type
    ):
        self._is_none = isinstance(None, received_type)
        message = f"Value of type {received_type.__name__} is not supported. "
        if isinstance(expected_type, Iterable):
            message += (
                f"Expected one of: {[arg.__name__ for arg in expected_type]}."
            )
        else:
            message += f"Expected type: {expected_type.__name__}."
        if self._is_none:
            type_hint = (
                f"Union{[type_.__name__ for type_ in expected_type]}"
                if isinstance(expected_type, Iterable)
                else expected_type.__name__
            )
            message += (
                " Specify a default value or "
                f"use Optional[{type_hint}] instead."
            )
        super().__init__(message)


class TimeoutException(DeclarativeException):
    def __init__(self, timeout: Union[int, None], request: httpx.Request):
        super().__init__(
            f"Request timed out after {timeout} seconds: "
            f"{request.method} {request.url}"
        )
