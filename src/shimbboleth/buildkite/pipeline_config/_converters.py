from typing import Annotated, Callable, Literal, Never, TypeAlias
from uuid import UUID

from shimbboleth.buildkite.pipeline_config._types import ExitStatus
from shimbboleth.internal.clay.validation import Not, ValidationError

# @TODO: Move these to clay
EmptyList: TypeAlias = list[Never]
EmptyDict: TypeAlias = dict[str, Never]

def bk_str(value: str | int | EmptyList | EmptyDict | None) -> str | None:
    if value is None:
        return None
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, list):
        if value:
            raise ValidationError(value, expectation="be an empty list")
        return None
    elif isinstance(value, dict):
        if value:
            raise ValidationError(value, expectation="be an empty dictionary")
        return None
    else:
        return value


def bk_key(value: Annotated[str, Not[UUID]] | int | EmptyList | EmptyDict | None) -> str | None:
    """Converter for key fields that validates against UUIDs."""
    if isinstance(value, str):
        try:
            UUID(value)
        except ValueError:
            pass
        else:
            raise ValidationError(value, expectation="not be a valid UUID")
    return bk_str(value)


def bk_bool(*, default: bool) -> Callable[[bool | Literal["true", "false"] | None], bool]:
    def bk_bool(value: bool | Literal["true", "false"] | None) -> bool:
        if value is None:
            return default
        if value in (True, "true"):
            return True
        elif value in (False, "false"):
            return False
        else:
            raise ValueError(f"Invalid value for bool: {value}")
    return bk_bool


def if_condition_converter(value: str | EmptyList | EmptyDict | None) -> str | None:
    """Converter for if_condition field that handles empty containers."""
    if isinstance(value, (list, dict)):
        if value:
            raise ValidationError(value, expectation="be an empty list/dict")
        return None
    return value


def convert_skip(value: bool | Literal["true", "false", ""] | str | None) -> bool | str:
    """Converter for Buildkite's 'skip' type."""
    if value in (True, "true"):
        return True
    elif value in (None, False, "false", ""):
        return False
    else:
        return value


def convert_bk_str_list(value: list[int | str] | str | int | None) -> list[str]:
    """Converter for Buildkite's 'list of strings' type."""
    if isinstance(value, list):
        return [str(item) for item in value]
    elif value is not None:
        return [str(value)]
    else:
        return []


def convert_soft_fail(value: bool | Literal["true", "false"] | list[int] | None) -> bool | list:
    """Converter for Buildkite's 'soft-fail' type."""
    if value in (True, "true"):
        return True
    elif value in (False, "false", None):
        return False
    elif value == []:
        return False
    elif isinstance(value, list) and any(status.exit_status == "*" for status in value if hasattr(status, 'exit_status')):
        return True
    elif isinstance(value, list):
        return [ExitStatus(exit_status=status) for status in value]
    else:
        return value
