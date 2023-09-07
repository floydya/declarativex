import inspect
from string import Formatter
from typing import Any, Callable, Dict, Iterator, List

from .compatibility import Field
from .dependencies import BaseParam, Path, Query


def extract_variables_from_url(template: str) -> List[str]:
    return [field[1] for field in Formatter().parse(template) if field[1]]


def get_default_args(func: Callable, path: str, **values) -> Dict[str, Field]:
    signature = inspect.signature(func)
    url_template_variables = extract_variables_from_url(path)
    fields = {}
    for key, val in signature.parameters.items():
        if val.default is not inspect.Parameter.empty and isinstance(
            val.default, BaseParam
        ):
            fields[key] = Field(
                location=val.default,
                type=func.__annotations__.get(key),
                value=values.get(key),
                name=val.default.field_name if val.default.field_name else key,
            )
        else:
            fields[key] = Field(
                location=Path() if key in url_template_variables else Query(),
                type=func.__annotations__.get(key),
                value=values.get(key),
                name=key,
            )
    return fields


def get_params(
    func: Callable[..., Any], path: str, **values: Any
) -> Iterator[Field]:
    for key, options in get_default_args(func, path, **values).items():
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
