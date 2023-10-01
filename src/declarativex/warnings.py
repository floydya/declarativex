import warnings
from typing import Type


class DeclarativeWarning(Warning):
    """Base class for all DeclarativeX warnings."""

    LIST_RETURN_TYPE = "Return type should be List[{t}] instead of {t}"
    NO_TYPE_HINT = "Type hint missing for '{f}'. Type validation skipped."
    UNSUPPORTED_CAST = (
        "Unsupported cast to {t}. Raw dictionary will be returned."
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


def warn_unsupported_cast(type_hint: Type) -> None:
    warnings.warn(
        DeclarativeWarning.UNSUPPORTED_CAST.format(t=type_hint.__name__),
        category=DeclarativeWarning,
    )
