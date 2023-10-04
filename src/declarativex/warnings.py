import warnings
from typing import Type


class DeclarativeWarning(Warning):
    """Base class for all DeclarativeX warnings."""

    LIST_RETURN_TYPE = "Return type should be List[{t}] instead of {t}"
    NO_TYPE_HINT = "Type hint missing for '{f}'. Type validation skipped."
    SUPPORT_DECORATOR_IGNORED = (
        "{d} decorator is ignored because not applied to endpoint declaration."
    )


def warn_list_return_type(type_hint: Type) -> None:
    warnings.warn(
        DeclarativeWarning.LIST_RETURN_TYPE.format(t=type_hint.__name__),
        category=DeclarativeWarning,
    )


def warn_no_type_hint(field_name: str):
    warnings.warn(
        DeclarativeWarning.NO_TYPE_HINT.format(f=field_name),
        category=DeclarativeWarning,
    )


def warn_support_decorator_ignored(decorator_class: str):
    warnings.warn(
        DeclarativeWarning.SUPPORT_DECORATOR_IGNORED.format(d=decorator_class),
        category=DeclarativeWarning,
    )
