import dataclasses
import inspect
import json
from json import JSONDecodeError
from typing import (
    Any,
    Callable,
    Dict,
    Optional,
    Sequence,
    Type,
    List,
    get_origin,
    TypeVar,
    get_args,
)
from urllib.parse import urljoin

import httpx

from .client import BaseClient
from .compatibility import parse_obj_as
from .dependencies import RequestModifier
from .exceptions import MisconfiguredException, UnprocessableEntityException
from .middlewares import Middleware
from .utils import ReturnType, SUPPORTED_METHODS
from .warnings import warn_list_return_type

T = TypeVar("T")


@dataclasses.dataclass
class Response:
    """
    Wrapper around httpx.Response that provides a method to convert the
    response to a specific type.

    Parameters:
        response: The response to wrap.

    Methods:
        as_type: Convert the response to a specific type.
        as_type_for_func: Convert the response to the return type of function.
    """
    response: httpx.Response

    @staticmethod
    def __replace_type_var(type_hint: Type, replacement: Type):
        """
        Replace a TypeVar with a concrete type. If the type hint is a list
        of TypeVars, replace the TypeVar in the list with the concrete type.
        """
        if isinstance(type_hint, TypeVar):
            return replacement
        if get_origin(type_hint) is list and isinstance(
            get_args(type_hint)[0], TypeVar
        ):
            return List[replacement]  # type: ignore[valid-type]
        return type_hint

    @classmethod
    def _dataclass_from_dict(
        cls, dataclass_type: Type[T], generic: Type, data: Dict[str, Any]
    ) -> T:
        """
        Create a dataclass from a dictionary. This method will recursively
        create dataclasses for fields that are dataclasses. If the dataclass
        has a generic type, the generic type will be replaced with the
        concrete type.
        """
        field_types = {
            f.name: cls.__replace_type_var(f.type, generic)
            for f in dataclasses.fields(
                dataclass_type  # type: ignore[arg-type]
            )
        }

        # Recursively update fields that are dataclasses
        for name, field_type in field_types.items():
            if "__origin__" in dir(field_type) and issubclass(
                field_type.__origin__, list
            ):
                elem_type = field_type.__args__[0]
                if dataclasses.is_dataclass(elem_type):
                    data[name] = [
                        cls._dataclass_from_dict(
                            elem_type, Any, elem  # type: ignore[arg-type]
                        )
                        for elem in data[name]
                    ]
            elif dataclasses.is_dataclass(field_type):
                data[name] = cls._dataclass_from_dict(
                    field_type, Any, data[name]  # type: ignore[arg-type]
                )

        return dataclass_type(
            **{k: v for k, v in data.items() if k in field_types}
        )

    def as_type(self, type_hint: Type):
        """
        Convert the response to a specific type. Supports dataclasses,
        pydantic models, dictionaries and lists of them.
        """
        self.response.raise_for_status()
        if type_hint is None or type_hint is inspect.Signature.empty:
            # If the type hint is None or inspect.Signature.empty, return the
            # httpx.Response as is.
            return self.response
        try:
            # Try to parse the response as JSON
            raw_response = json.loads(self.response.text)
        except JSONDecodeError as e:
            # If the response is not JSON, raise an exception
            raise UnprocessableEntityException(response=self.response) from e
        return_type = type_hint
        outer_type = get_origin(type_hint)
        is_list = outer_type == list
        inner_type = get_args(type_hint)[0] if is_list else type_hint
        if isinstance(raw_response, list) and not is_list:
            # If the response is a list, but the type hint is not, show a
            # warning and apply the type hint to the list.
            warn_list_return_type(type_hint)
            return_type = List[type_hint]  # type: ignore[valid-type]

        if dataclasses.is_dataclass(outer_type):
            # If the type hint is a dataclass, create a dataclass from the
            # response.
            generic_args = get_args(inner_type)
            generic_type = generic_args[0] if generic_args else None
            return self._dataclass_from_dict(
                outer_type,  # type: ignore[arg-type]
                generic_type,
                data=raw_response
            )

        # In other cases, parse the response as the type hint.
        return parse_obj_as(return_type, raw_response)

    def as_type_for_func(self, func: Callable[..., ReturnType]) -> ReturnType:
        """
        Convert the response to the return type of function.
        """
        return_type: type = inspect.signature(func).return_annotation
        return self.as_type(return_type)


@dataclasses.dataclass
class ClientConfiguration:
    """
    Configuration for a client. This class is used to configure the client
    with default values for query parameters, headers, middlewares and
    error mappings. The configuration can be passed to the client as a
    parameter or as a class attribute.
    """
    base_url: Optional[str] = dataclasses.field(default=None)
    default_query_params: Dict[str, Any] = dataclasses.field(
        default_factory=dict
    )
    default_headers: Dict[str, str] = dataclasses.field(default_factory=dict)
    middlewares: Sequence[Middleware] = dataclasses.field(default_factory=list)
    error_mappings: Dict[int, Type] = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        """
        Validate the configuration. Raises an exception if the configuration
        is invalid.
        """
        if not isinstance(self.default_query_params, dict):
            # default_query_params should be a dictionary
            raise MisconfiguredException(
                "default_query_params must be a dictionary"
            )
        if not isinstance(self.default_headers, dict):
            # default_headers should be a dictionary
            raise MisconfiguredException(
                "default_headers must be a dictionary"
            )
        if not isinstance(self.middlewares, list):
            # middlewares should be a list
            raise MisconfiguredException("middlewares must be a list")
        if not isinstance(self.error_mappings, dict):
            # error_mappings should be a dictionary
            raise MisconfiguredException("error_mappings must be a dictionary")

    @classmethod
    def extract_from_func_kwargs(
        cls, self_: Optional[BaseClient], cls_: Optional[BaseClient]
    ) -> Optional["ClientConfiguration"]:
        """
        Extract the configuration from the function bounded to class.
        If function is not bounded to class, return None.
        """
        if self_ or cls_:
            cls_instance: BaseClient = (
                self_ or cls_  # type: ignore[assignment]
            )
            return cls.create(
                base_url=cls_instance.base_url,
                default_query_params=cls_instance.default_query_params,
                default_headers=cls_instance.default_headers,
                middlewares=cls_instance.middlewares,
                error_mappings=cls_instance.error_mappings,
            )
        return None

    def merge(self, other: "ClientConfiguration") -> "ClientConfiguration":
        """
        Merge two configurations. The values of the other configuration
        take precedence over the values of this configuration.
        """
        return ClientConfiguration(
            base_url=other.base_url or self.base_url,
            default_query_params={
                **other.default_query_params,
                **self.default_query_params,
            },
            default_headers={**other.default_headers, **self.default_headers},
            middlewares=[*other.middlewares, *self.middlewares],
            error_mappings={**other.error_mappings, **self.error_mappings},
        )

    @classmethod
    def create(cls, **values) -> "ClientConfiguration":
        """
        Create a configuration from a dictionary. The dictionary can contain
        any of the attributes of the configuration. If an attribute is not
        present in the dictionary, the default value will be used.
        """
        return cls(**{k: val for k, val in values.items() if val is not None})


@dataclasses.dataclass
class EndpointConfiguration:
    """
    Configuration for an endpoint. This class is used to configure the
    endpoint with a method, path, timeout and client configuration.
    """
    client_configuration: ClientConfiguration
    method: str
    path: str
    timeout: Optional[float] = dataclasses.field(default=5.0)

    @property
    def url_template(self):
        """
        The URL template for the endpoint. The URL template is the base URL
        of the client configuration joined with the path of the endpoint
        configuration.
        """
        return urljoin(self.client_configuration.base_url, self.path)

    def __post_init__(self):
        """
        Validate the configuration. Raises an exception if the configuration
        is invalid. The method must be one of the supported methods. The
        timeout must be a non-negative number.
        """
        self.method = self.method.upper()
        if self.method not in SUPPORTED_METHODS:
            methods = sorted(list(SUPPORTED_METHODS))
            raise MisconfiguredException(f"method must be one of {methods}")
        if self.timeout and self.timeout < 0:
            # Negative timeout? Really?
            raise MisconfiguredException(
                "timeout must be a non-negative number"
            )


@dataclasses.dataclass
class RawRequest:
    """
    A raw request. This class is used to configure a request with a method,
    URL template, path parameters, query parameters, headers, cookies, JSON
    body and timeout. The request can be prepared with a function and
    arguments. The function signature is used to modify the request
    before it is sent.
    """
    method: str
    url_template: str
    path_params: Dict[str, str] = dataclasses.field(default_factory=dict)
    query_params: Dict[str, Any] = dataclasses.field(default_factory=dict)
    headers: Dict[str, str] = dataclasses.field(default_factory=dict)
    cookies: Dict[str, str] = dataclasses.field(default_factory=dict)
    json: Dict[str, Any] = dataclasses.field(default_factory=dict)
    timeout: Optional[float] = None

    @classmethod
    def initialize(
        cls,
        endpoint_configuration: EndpointConfiguration,
    ) -> "RawRequest":
        """
        Initialize a request from an endpoint configuration. The request
        will be initialized with the default query parameters and headers
        of the client configuration.
        """
        q = endpoint_configuration.client_configuration.default_query_params
        h = endpoint_configuration.client_configuration.default_headers
        return RawRequest(
            method=endpoint_configuration.method,
            url_template=endpoint_configuration.url_template,
            query_params=q,
            headers=h,
        )

    def prepare(self, func: Callable, **values) -> "RawRequest":
        """
        Prepare the request with a function and arguments. The function
        signature is used to modify the request before it is sent.
        """
        return RequestModifier.prepare_request(
            request=self, func=func, **values
        )

    def url(self):
        return self.url_template.format(**self.path_params)

    def to_httpx_request(self) -> httpx.Request:
        """Convert the request to a httpx.Request."""
        return httpx.Request(
            method=self.method,
            url=self.url(),
            params=self.query_params,
            headers=self.headers,
            cookies=self.cookies,
            json=self.json,
        )
