from typing import Annotated, Callable, Literal, Never, TypeAlias
from uuid import UUID

from shimbboleth.internal.clay.validation import Not, ValidationError

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


def depends_on_converter(value: Annotated[str, Not[""]] | int | list[str | int | dict] | None) -> list:
    """Converter for depends_on field that handles various input types."""
    # Import here to avoid circular imports
    from shimbboleth.buildkite.pipeline_config.step import Step
    
    if isinstance(value, str):
        if not value:
            raise ValidationError(value, expectation="not be an empty string")
        return [Step.Dependency(step=value)]
    elif isinstance(value, int):
        return [Step.Dependency(step=str(value))]
    elif isinstance(value, list):
        coerced = []
        for index, elem in enumerate(value):
            with ValidationError.context(index=index):
                if isinstance(elem, str):
                    if not elem:
                        raise ValidationError(elem, expectation="not be an empty string")
                    coerced.append(Step.Dependency(step=elem))
                elif isinstance(elem, int):
                    coerced.append(Step.Dependency(step=str(elem)))
                elif isinstance(elem, dict):
                    coerced.append(Step.Dependency(**elem))
                elif hasattr(elem, 'step'):  # Already a Step.Dependency
                    coerced.append(elem)
                else:
                    raise ValidationError(elem, expectation="be a string, int, dict, or Step.Dependency")
        return coerced
    elif value is None:
        return []
    else:
        raise ValidationError(value, expectation="be a string, int, list, or None")


def if_condition_converter(value: str | EmptyList | EmptyDict | None) -> str | None:
    """Converter for if_condition field that handles empty containers."""
    if isinstance(value, (list, dict)):
        if value:
            raise ValidationError(value, expectation="be an empty list/dict")
        return None
    return value
