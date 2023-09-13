from collections.abc import Iterable
from typing import Type, Sequence, Union, Mapping, Optional, TYPE_CHECKING, Any

import httpx

from .compatibility import parse_obj_as

if TYPE_CHECKING:  # pragma: no cover
    from .models import RawRequest


class DeclarativeException(Exception):
    pass


class MisconfiguredException(DeclarativeException):
    pass


class DependencyValidationError(DeclarativeException):

    @classmethod
    def _name_accessor(cls, entity: Any) -> str:  # pragma: no cover
        if hasattr(entity, "__name__"):
            return entity.__name__
        return str(entity)

    def __init__(
        self, expected_type: Union[Type, Sequence[Type]], received_type: Type
    ):
        self._is_none = isinstance(None, received_type)
        message = f"Value of type {received_type.__name__} is not supported. "
        if isinstance(expected_type, Iterable):
            names = [self._name_accessor(arg) for arg in expected_type]
            message += (
                f"Expected one of: {names}."
            )
        else:
            message += f"Expected type: {self._name_accessor(expected_type)}."
        if self._is_none:
            names = [self._name_accessor(type_) for type_ in expected_type]
            type_hint = (
                f"Union{names}"
                if isinstance(expected_type, Iterable)
                else self._name_accessor(expected_type)
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
        raw_request: "RawRequest",
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


class UnprocessableEntityException(DeclarativeException):
    def __init__(self, response: httpx.Response):
        self.response = response
        super().__init__(
            f"Failed to parse response. Status code: {response.status_code}. "
            "You can access the raw response using the `response` attribute."
        )
