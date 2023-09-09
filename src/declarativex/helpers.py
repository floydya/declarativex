import inspect
from string import Formatter
from typing import Callable, Iterator, List

from .dependencies import Dependency, Path, Query


def extract_variables_from_url(template: str) -> List[str]:
    return [field[1] for field in Formatter().parse(template) if field[1]]


def get_params(func: Callable, path: str, **values) -> Iterator[Dependency]:
    signature = inspect.signature(func)
    url_template_variables = extract_variables_from_url(path)
    for key, val in signature.parameters.items():
        if key in ["self", "cls"]:
            continue
        if val.default is not inspect.Parameter.empty and issubclass(
            val.default.__class__, Dependency
        ):
            field = val.default
        elif key in url_template_variables:
            field = Path(...)
        else:
            field = Query(...)
        yield field.prepare(
            key, func.__annotations__.get(key), values.get(key)
        )
