from collections.abc import Iterable
from typing import Type, Sequence, Union, Mapping, Optional, TYPE_CHECKING

import httpx

from .compatibility import parse_obj_as

if TYPE_CHECKING:  # pragma: no cover
    from .request import RequestDict


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
    def __init__(self, timeout: Union[float, None], request: httpx.Request):
        super().__init__(
            f"Request timed out after {timeout} seconds: "
            f"{request.method} {request.url}"
        )


class HTTPException(DeclarativeException):
    def __init__(
        self,
        request: httpx.Request,
        response: httpx.Response,
        raw_request: "RequestDict",
        error_mappings: Optional[Mapping[int, Type]] = None,
    ):
        self.request = request
        self.raw_request = raw_request
        self._response = response
        self.__error_mappings = error_mappings or {}
        self._model = None
        self.status_code = response.status_code
        if response.status_code in self.__error_mappings:
            self._model = self.__error_mappings[response.status_code]
        super().__init__(
            f"Request failed with status code {response.status_code}: "
            f"{request.method} {request.url}"
        )

    @property
    def response(self):
        response = self._response.json()
        if self._model:
            return parse_obj_as(self._model, response)
        return response
