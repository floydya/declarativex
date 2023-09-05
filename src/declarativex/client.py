import inspect
import warnings
from string import Formatter
from typing import Any, Callable, Generic, Iterator, Optional, TypeVar

import httpx
from pydantic import BaseModel

from .compatibility import parse_obj, to_dict
from .dependencies import BaseParam, BodyField, Json, Path, Query


ParamType = TypeVar("ParamType", bound=BaseParam)

with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=DeprecationWarning)

    # Compatible with pydantic v1 and v2
    class Field(Generic[ParamType], BaseModel):
        location: ParamType
        type: Any
        value: Any
        name: str

        class Config:
            arbitrary_types_allowed = True


class BaseClient:
    """
    Base class for declarative HTTP clients.

    Parameters:
        base_url: Base URL for the client.
        headers: Default headers for the client.
        default_query_params: Default query parameters for the client.
    """

    def __init__(
        self,
        base_url: str,
        headers: Optional[dict[str, str]] = None,
        default_query_params: Optional[dict[str, Any]] = None,
    ) -> None:
        self.base_url = base_url
        self.headers = headers or {}
        self.default_query_params = default_query_params or {}

    @staticmethod
    def _extract_variables_from_url(template: str):
        return [field[1] for field in Formatter().parse(template) if field[1]]

    @classmethod
    def _get_default_args(cls, func: Callable, kwargs) -> dict[str, Field]:
        signature = inspect.signature(func)
        url_template_variables = cls._extract_variables_from_url(
            getattr(func, "_path")
        )
        fields = {}
        for key, val in signature.parameters.items():
            if val.default is not inspect.Parameter.empty and isinstance(
                val.default, BaseParam
            ):
                fields[key] = Field(
                    location=val.default,
                    type=func.__annotations__.get(key),
                    value=kwargs.get(key),
                    name=val.default.field_name
                    if val.default.field_name
                    else key,
                )
            else:
                fields[key] = Field(
                    location=Path()
                    if key in url_template_variables
                    else Query(),
                    type=func.__annotations__.get(key),
                    value=kwargs.get(key),
                    name=key,
                )
        return fields

    def _get_params(self, func: Callable, **kwargs: Any) -> Iterator[Field]:
        for key, options in self._get_default_args(func, kwargs).items():
            # Apply default value if parameter is optional and not provided
            if options.value is None:
                options.value = options.location.default

            # Raise error if PATH parameter is required and not provided
            if isinstance(options.location, Path):
                if options.value is None:
                    raise ValueError(
                        f"Parameter with {key=} is required and has no default"
                    )
            # Skip if QUERY parameter is not provided and no default value
            elif isinstance(options.location, Query):
                if options.value is None:
                    continue
            yield options

    def validate_func(self, func: Callable) -> None:
        ...

    def prepare_request(
        self, func: Callable, **kwargs: Any
    ) -> tuple[dict[str, Any], str, Optional[dict[str, Any]], dict[str, str]]:
        path = getattr(func, "_path")

        params = self.default_query_params.copy()
        body = {}
        data = None
        url = f"{self.base_url}{path}"
        for options in self._get_params(func, **kwargs):
            if isinstance(options.location, Path):
                url = url.format(**{options.name: options.value})
            elif isinstance(options.location, Query):
                params[options.name] = options.value
            elif isinstance(options.location, BodyField):
                body[options.name] = options.value
            elif isinstance(options.location, Json):
                data = (
                    to_dict(options.value)
                    if isinstance(options.value, BaseModel)
                    else options.value
                )

        data = (data or {}) | body
        return params, url, data, self.headers

    @staticmethod
    def process_response(response: httpx.Response, func: Callable) -> Any:
        return_type = func.__annotations__.get("return")

        json_response = response.json()
        if not return_type:
            return json_response
        if isinstance(json_response, dict) and issubclass(
            return_type, BaseModel
        ):
            return parse_obj(return_type, json_response)
        if isinstance(json_response, list):
            if return_type.__args__ and issubclass(
                return_type.__args__[0], BaseModel
            ):
                return [
                    parse_obj(return_type.__args__[0], item)
                    for item in json_response
                ]
        return json_response


__all__ = ["BaseClient"]
