import abc
import dataclasses
import enum
import inspect
import json
from string import Formatter
from typing import (
    Any,
    Callable,
    List,
    Optional,
    TYPE_CHECKING,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

from pydantic import BaseModel

from .compatibility import to_dict
from .exceptions import (
    AnnotationException,
    DependencyValidationError,
    MisconfiguredException,
)
from .warnings import warn_no_type_hint

if TYPE_CHECKING:
    from .models import RawRequest


Value = TypeVar("Value")


class Location(str, enum.Enum):
    """Enum for dependency locations."""

    path_params = "path_params"
    query_params = "query_params"
    headers = "headers"
    cookies = "cookies"
    json = "json"
    timeout = "timeout"


class Dependency(abc.ABC):
    """
    Base class for all dependencies. Dependencies are used to modify requests
    before they are sent to the server.

    :arg field_name: The name of the field to modify.
    :type field_name: str
    """

    location: Location
    _field_name: str
    _value: Any
    _type_hint: Optional[Type] = None

    def __init__(
        self,
        *,
        field_name: Union[str, None] = None,
    ):
        self._overridden_field_name = field_name

    @property
    def type_hint(self) -> Union[Type[Value], None]:
        """The type hint for the dependency."""
        return self._type_hint

    @type_hint.setter
    def type_hint(self, value: Union[Type[Value], None]) -> None:
        """Set the type hint for the dependency."""
        self._type_hint = value

    @property
    def field_name(self) -> str:
        """The name of the field to modify."""
        return self._overridden_field_name or self._field_name

    @field_name.setter
    def field_name(self, value: str) -> None:
        """Set the name of the field to modify."""
        self._field_name = value

    @property
    def value(self) -> Any:
        """The value to set the field to."""
        return self._value

    @value.setter
    def value(self, value: Any) -> None:
        """Set the value to set the field to."""
        self._value = self.validate(value)

    def validate(self, value: Any) -> Any:
        """
        Validate the value against the type hint.
        :param value: The value to validate.
        :return: The value if it is valid.
        """
        if self.type_hint:
            return self.__validate_type_hint(value)
        # If no type hint is provided, we can't validate the value.
        # We show a warning instead and return the original value.
        warn_no_type_hint(self.field_name)
        return value

    def __validate_type_hint(self, value: Any) -> Any:
        """
        Validate the value against the type hint.
        :param value: The value to validate.
        :return: The value if it is valid.
        """
        if get_origin(self.type_hint) is Union:
            # To check union type hints we need to obtain the Union args.
            return self.__validate_union_type_hint(value)
        if not isinstance(value, self.type_hint):  # type: ignore[arg-type]
            # If the value is not an instance of the type hint, we raise a
            # DependencyValidationError.
            raise DependencyValidationError(
                expected_type=self.type_hint,  # type: ignore[arg-type]
                received_type=type(value),
            )
        # If the value is valid, we return it.
        return value

    def __validate_union_type_hint(self, value: Any) -> Any:
        """
        Validate the value against a union type hint.
        :param value: The value to validate.
        :return: The value if it is valid.
        """
        args = get_args(self.type_hint)
        # Checking if the value is an instance of the union args.
        if not any(isinstance(value, arg) for arg in args):
            raise DependencyValidationError(
                expected_type=args, received_type=type(value)
            )
        # If the value is valid, we return it.
        return value

    def modify_request(self, request: "RawRequest") -> "RawRequest":
        """
        Modify the request.
        :param request: The request to modify.
        :return: The modified request.
        """
        data = getattr(request, self.location.value)
        data[self.field_name] = self.value
        setattr(request, self.location.value, data)
        return request

    def __repr__(self):  # pragma: no cover
        return f"{self.__class__.__name__}"

    def __str__(self):  # pragma: no cover
        return f"{self.__class__.__name__}(field_name={self.field_name})"


class Path(Dependency):
    """
    Dependency for path parameters. Path parameters are
    extracted from the URL template.
    """
    location = Location.path_params


class Query(Dependency):
    """Dependency for query parameters."""
    location = Location.query_params


class Header(Dependency):
    """
    Dependency for headers. The field name is mandatory for headers.
    The field name is converted to lowercase automatically.
    """
    location = Location.headers

    def __init__(self, *, name: str):
        """Field name is mandatory for headers."""
        super().__init__(field_name=name.lower())


class Cookie(Dependency):
    """Dependency for cookies."""
    location = Location.cookies


class JsonField(Dependency):
    """Dependency for JSON fields."""
    location = Location.json


class Json(Dependency):
    """
    Dependency for JSON. The value can be a BaseModel,
    a dataclass, a dict or a JSON string.
    """
    location = Location.json

    def __init__(self):
        """Field name is unused for Json."""
        super().__init__()

    def modify_request(self, request: "RawRequest") -> "RawRequest":
        """
        Modify the request. If the value is a BaseModel or a dataclass, the
        fields of the value are merged with the JSON data.
        :param request: The request to modify.
        :return: The modified request.
        """
        data = getattr(request, self.location.value)
        if isinstance(self.value, BaseModel):
            # If the value is a BaseModel, we convert it to
            # a dict and merge it with the JSON data.
            data = {**data, **to_dict(self.value)}
        elif dataclasses.is_dataclass(self.value):
            # If the value is a dataclass, we convert it to
            # a dict and merge it with the JSON data.
            data = {**data, **dataclasses.asdict(self.value)}
        elif isinstance(self.value, dict):
            # If the value is a dict, we merge it with the JSON data.
            data = {**data, **self.value}
        elif isinstance(self.value, str):
            # If the value is a JSON string, we merge it with the JSON data.
            try:
                data = {**data, **json.loads(self.value)}
            except ValueError as exc:
                # If the value is not a valid JSON string, we raise a
                # DependencyValidationError.
                raise DependencyValidationError(
                    expected_type=self.type_hint,  # type: ignore[arg-type]
                    received_type=str,
                ) from exc
        setattr(request, self.location.value, data)
        return request


class Timeout(Dependency):
    """
    Dependency for timeouts. The value is the timeout in seconds.
    """
    location = Location.timeout

    def modify_request(self, request: "RawRequest") -> "RawRequest":
        """
        Modify the request.
        :param request: The request to modify.
        :return: The modified request.
        """
        setattr(request, self.location.value, self.value)
        return request


class RequestModifier:
    """
    Class for modifying requests. This class is used internally by
    declarativex.
    """
    @staticmethod
    def __extract_variables_from_url_template(url_template: str) -> List[str]:
        """
        Extract variables from a URL template.
        :param url_template: The URL template.
        :return: The variables in the URL template.
        """
        return [
            field[1] for field in Formatter().parse(url_template) if field[1]
        ]

    @classmethod
    def prepare_request(
        cls, request: "RawRequest", func: Callable, **values
    ) -> "RawRequest":
        """
        Prepare a request for sending. This method is used internally by
        declarativex. It is called before the request is sent. It modifies the
        request according to the dependencies. It also validates the values
        against the type hints.
        :param request: The request to prepare.
        :param func: The function that is called.
        :param values: The values to set the dependencies to.
        :return: The prepared request.
        """
        signature = inspect.signature(func)
        url_template_variables = cls.__extract_variables_from_url_template(
            request.url_template
        )
        dependencies = []
        for key, val in signature.parameters.items():
            if key in ["self", "cls"]:
                # We don't need the self or cls parameter.
                continue

            # We check if the parameter is annotated.
            annotation = func.__annotations__.get(key, None)
            if hasattr(annotation, "__metadata__"):
                # Extracting the type hint and the dependency from the
                # Annotated type.
                type_hint, dependency = get_args(annotation)
                if not isinstance(dependency, Dependency):
                    if inspect.isclass(dependency) and issubclass(
                        dependency, Dependency
                    ):
                        # If the dependency is a class, we instantiate it.
                        dependency = dependency()
                        dependency.type_hint = type_hint
                    else:
                        # If the dependency is not an instance of Dependency,
                        # we raise an AnnotationException.
                        raise AnnotationException(annotation)
                else:
                    # If the dependency is already an instance of Dependency,
                    # we are setting only the type hint.
                    dependency.type_hint = type_hint
            elif key in url_template_variables:
                # If the parameter is in the URL template and not annotated,
                # we assume it is a Path dependency.
                dependency = Path()
                dependency.type_hint = annotation
            else:
                # If the parameter is not annotated and not in the URL
                # template, we assume it is a Query dependency.
                dependency = Query()
                dependency.type_hint = annotation

            # We set the field name and the value of the dependency.
            dependency.field_name = key
            dependency.value = values.get(key, val.default)
            dependencies.append(dependency)

        # We check if the request method is GET and if there are any Json
        # dependencies. If there are, we raise a MisconfiguredException.
        if request.method == "GET" and any(
            isinstance(dependency, (JsonField, Json))
            for dependency in dependencies
        ):
            raise MisconfiguredException(
                "BodyField and Json fields are not supported for GET requests"
            )

        # Modifying the request according to the dependencies in loop.
        for dependency in dependencies:
            request = dependency.modify_request(request)
        return request


__all__ = [
    "Dependency",
    "Path",
    "Query",
    "Header",
    "Cookie",
    "JsonField",
    "Json",
    "Timeout",
    "RequestModifier",
]
