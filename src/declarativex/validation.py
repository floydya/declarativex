from typing import get_origin, Union, Type, get_args, TypeVar

from .exceptions import DependencyValidationError

T = TypeVar("T")


def _validate_type_hint(type_hint: Type, value: T) -> T:
    """
    Validate the value against the type hint.
    :param type_hint: The type hint.
    :param value: The value to validate.
    :return: The value if it is valid.
    """
    if get_origin(type_hint) is Union:
        # To check union type hints we need to obtain the Union args.
        return _validate_union_type_hint(type_hint, value)
    if not isinstance(value, type_hint):  # type: ignore[arg-type]
        # If the value is not an instance of the type hint, we raise a
        # DependencyValidationError.
        raise DependencyValidationError(
            expected_type=type_hint,  # type: ignore[arg-type]
            received_type=type(value),
        )
    # If the value is valid, we return it.
    return value


def _validate_union_type_hint(type_hint: Type, value: T) -> T:
    """
    Validate the value against a union type hint.
    :param type_hint: The union type hint.
    :param value: The value to validate.
    :return: The value if it is valid.
    """
    args = get_args(type_hint)
    # Checking if the value is an instance of the union args.
    if not any(isinstance(value, arg) for arg in args):
        raise DependencyValidationError(
            expected_type=args, received_type=type(value)
        )
    # If the value is valid, we return it.
    return value
