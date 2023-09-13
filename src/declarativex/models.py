import dataclasses
import inspect
from json import JSONDecodeError
from typing import (
    Any,
    Callable,
    Dict,
    Optional,
    Sequence,
    Type,
    Union,
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
from .middlewares import AsyncMiddleware, Middleware
from .utils import ReturnType, SUPPORTED_METHODS
from .warnings import warn_list_return_type

T = TypeVar("T")


@dataclasses.dataclass
class Response:
    response: httpx.Response

    @staticmethod
    def __replace_type_var(type_hint: Type, replacement: Type):
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
        self.response.raise_for_status()
        if type_hint is None or type_hint is inspect.Signature.empty:
            return self.response
        try:
            raw_response = self.response.json()
        except JSONDecodeError as e:
            raise UnprocessableEntityException(response=self.response) from e
        return_type = type_hint
        outer_type = get_origin(type_hint)
        is_list = outer_type == list
        inner_type = get_args(type_hint)[0] if is_list else type_hint
        if isinstance(raw_response, list) and not is_list:
            warn_list_return_type(type_hint)
            return_type = List[type_hint]  # type: ignore[valid-type]

        if dataclasses.is_dataclass(outer_type):
            generic_args = get_args(inner_type)
            generic_type = generic_args[0] if generic_args else None
            return self._dataclass_from_dict(
                outer_type,  # type: ignore[arg-type]
                generic_type,
                data=raw_response
            )

        return parse_obj_as(return_type, raw_response)

    def as_type_for_func(self, func: Callable[..., ReturnType]) -> ReturnType:
        return_type: type = inspect.signature(func).return_annotation
        return self.as_type(return_type)


@dataclasses.dataclass
class ClientConfiguration:
    base_url: Optional[str] = dataclasses.field(default=None)
    default_query_params: Dict[str, Any] = dataclasses.field(
        default_factory=dict
    )
    default_headers: Dict[str, str] = dataclasses.field(default_factory=dict)
    middlewares: Sequence[
        Union[Middleware, AsyncMiddleware]
    ] = dataclasses.field(default_factory=list)
    error_mappings: Dict[int, Type] = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.default_query_params, dict):
            raise MisconfiguredException(
                "default_query_params must be a dictionary"
            )
        if not isinstance(self.default_headers, dict):
            raise MisconfiguredException(
                "default_headers must be a dictionary"
            )
        if not isinstance(self.middlewares, list):
            raise MisconfiguredException("middlewares must be a list")
        if not isinstance(self.error_mappings, dict):
            raise MisconfiguredException("error_mappings must be a dictionary")

    @classmethod
    def extract_from_func_kwargs(
        cls, self_: Optional[BaseClient], cls_: Optional[BaseClient]
    ) -> Optional["ClientConfiguration"]:
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
        return cls(**{k: val for k, val in values.items() if val is not None})


@dataclasses.dataclass
class EndpointConfiguration:
    client_configuration: ClientConfiguration
    method: str
    path: str
    timeout: Optional[float] = dataclasses.field(default=5.0)

    @property
    def url_template(self):
        return urljoin(self.client_configuration.base_url, self.path)

    def __post_init__(self):
        self.method = self.method.upper()
        if self.method not in SUPPORTED_METHODS:
            methods = sorted(list(SUPPORTED_METHODS))
            raise MisconfiguredException(f"method must be one of {methods}")
        if self.timeout and self.timeout < 0:
            raise MisconfiguredException(
                "timeout must be a non-negative number"
            )


@dataclasses.dataclass
class RawRequest:
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
        q = endpoint_configuration.client_configuration.default_query_params
        h = endpoint_configuration.client_configuration.default_headers
        return RawRequest(
            method=endpoint_configuration.method,
            url_template=endpoint_configuration.url_template,
            query_params=q,
            headers=h,
        )

    def prepare(self, func: Callable, **values) -> "RawRequest":
        return RequestModifier.prepare_request(
            request=self, func=func, **values
        )

    def to_httpx_request(self) -> httpx.Request:
        return httpx.Request(
            method=self.method,
            url=self.url_template.format(**self.path_params),
            params=self.query_params,
            headers=self.headers,
            cookies=self.cookies,
            json=self.json,
        )
