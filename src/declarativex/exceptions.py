from collections.abc import Iterable
from typing import Type, Sequence, Union, Mapping, Optional, TYPE_CHECKING, Any

import httpx

from .compatibility import parse_obj_as

if TYPE_CHECKING:  # pragma: no cover
    from .models import RawRequest


class DeclarativeException(Exception):
    """Base class for all declarativex exceptions."""


class MisconfiguredException(DeclarativeException):
    """Raised when a client is misconfigured."""


class AnnotationException(MisconfiguredException):
    """
    Raised when an unsupported annotation is used.

    Parameters:
        annotation(`Type`): The annotation that was used.
    """
    def __init__(self, annotation: Type):
        super().__init__(
            f"Annotation {annotation} is not supported. "
            "Use Annotated[type, Dependency] instead."
        )


class DependencyValidationError(DeclarativeException):
    """
    Raised when a dependency cannot be validated.

    Parameters:
        expected_type(`Union[Type, Sequence[Type]]`):
            The dependency that failed validation.
        received_type(`Type`): The type that was received.
    """
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
    """
    Raised when a request times out.

    Parameters:
        timeout(`Optional[float]`): The timeout in seconds.
        request(`httpx.Request`): The request that timed out.
    """
    def __init__(self, timeout: Union[float, None], request: httpx.Request):
        super().__init__(
            f"Request timed out after {timeout} seconds: "
            f"{request.method} {request.url}"
        )


class HTTPException(DeclarativeException):
    """
    Raised when a request fails with HTTP status code.

    Parameters:
        request(`httpx.Request`): The request that failed.
        response(`httpx.Response`): The response that was received.
        raw_request(`RawRequest`): The raw request that was sent.
        error_mappings(`Mapping[int, Type]`):
            A mapping of status codes to error models.
    """
    raw_request: "RawRequest"
    status_code: int
    _response: httpx.Response
    _model: Optional[Type] = None

    def __init__(
        self,
        request: httpx.Request,
        response: httpx.Response,
        raw_request: "RawRequest",
        error_mappings: Optional[Mapping[int, Type]] = None,
    ):
        self.raw_request = raw_request
        self._response = response
        self.status_code = response.status_code
        if error_mappings and response.status_code in error_mappings:
            self._model = error_mappings[response.status_code]
        super().__init__(
            f"Request failed with status code {response.status_code}: "
            f"{request.method} {request.url}"
        )

    @property
    def response(self):
        """
        The response that was received. If a model is specified, the response
        will be parsed and returned as an instance of that model.
        :return: httpx.Response or Instance of self._model
        """
        response = self._response
        if self._model:
            return parse_obj_as(self._model, response.json())
        return response


class UnprocessableEntityException(DeclarativeException):
    """
    Raised when a request fails when parsing of the response fails.

    Parameters:
        response(`httpx.Response`): The response that was received.
    """
    def __init__(self, response: httpx.Response):
        self.response = response
        super().__init__(
            f"Failed to parse response. Status code: {response.status_code}. "
            "You can access the raw response using the `response` attribute."
        )


class RateLimitExceeded(DeclarativeException):
    """
    Raised when a request fails due to rate limiting.
    """


__all__ = [
    "DeclarativeException",
    "MisconfiguredException",
    "AnnotationException",
    "DependencyValidationError",
    "TimeoutException",
    "HTTPException",
    "UnprocessableEntityException",
    "RateLimitExceeded",
]
