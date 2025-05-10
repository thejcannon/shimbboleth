from typing import Literal, overload, Generic, TypeVar, get_type_hints, TypeAlias, Any
from dataclasses import field
from shimbboleth.internal.clay.model import Model
from shimbboleth.internal.clay.json_schema import schema
from shimbboleth.internal.clay.jsonT import JSONObject

from shimbboleth.internal.clay.validation import ValidationError

T = TypeVar("T")

EmptyList: TypeAlias = list[Any]
EmptyDict: TypeAlias = dict[str, Any]


class _DescriptorBase(Generic[T]):
    def __set_name__(self, owner, name: str) -> None:
        self.name = name

    @overload
    def __get__(self, instance: None, owner) -> None: ...

    @overload
    def __get__(self, instance: object, owner) -> T: ...

    def __get__(self, instance, owner) -> T:
        if instance is None:
            return None
        return instance.__dict__[self.name]

    def __set__(self, instance, value) -> None:
        instance.__dict__[self.name] = value

    @classmethod
    def __shimbboleth_json_schema__(cls, *, model_defs: dict[str, JSONObject]):
        """Generate JSON schema based on the __set__ method's type hints."""
        if not hasattr(cls, "__set__"):
            raise TypeError(
                f"{cls.__name__} must have a __set__ method with type hints"
            )

        type_hints = get_type_hints(cls.__set__)
        if "value" not in type_hints:
            raise TypeError(
                f"{cls.__name__}.__set__ must have a 'value' parameter with type hints"
            )

        return schema(type_hints["value"], model_defs=model_defs)


class ExitStatus(Model, extra=True):
    exit_status: Literal["*"] | int
    """The exit status number that will cause this job to soft-fail"""


class BKStr(_DescriptorBase[str]):
    """
    A descriptor for Buildkite's "string" type.
    """

    def __init__(self, *, json_alias: str | None = None) -> None:
        self.json_alias = json_alias

    def __set__(self, instance, value: str | int | EmptyList | EmptyDict | None):
        if isinstance(value, int):
            value = str(value)
        elif isinstance(value, list):
            if value:
                raise ValidationError(value, expectation="be an empty list")
            value = None
        elif isinstance(value, dict):
            if value:
                raise ValidationError(value, expectation="be an empty dictionary")
            value = None
        super().__set__(instance, value)


class BKBool(_DescriptorBase[bool]):
    """
    A descriptor for Buildkite's "boolean" type.

    @TODO: Mention get/set types.
    """

    def __init__(self, *, default: bool, json_alias: str | None = None) -> None:
        self.default = default
        self.json_alias = json_alias

    def __get__(self, instance, owner) -> T:
        if instance is None:
            return self.default
        return instance.__dict__[self.name]

    def __set__(self, instance, value: bool | Literal["true", "false"] | None) -> None:
        if value is None:
            value = self.default
        if value in (True, "true"):
            value = True
        elif value in (False, "false"):
            value = False
        else:
            raise ValueError(f"Invalid value for bool: {value}")
        instance.__dict__[self.name] = value


class Skip(_DescriptorBase[bool | str]):
    """
    A descriptor for Buildkite's "skip" type.
    """

    def __set__(
        self, instance, value: bool | Literal["true", "false", ""] | str | None
    ) -> None:
        if value in (True, "true"):
            instance.__dict__[self.name] = True
        elif value in (None, False, "false", ""):
            instance.__dict__[self.name] = False
        else:
            instance.__dict__[self.name] = value


class BKStrList(_DescriptorBase[list[str]]):
    """
    A descriptor for Buildkite's "list of strings"
    """

    def __get__(self, instance, owner) -> T:
        if instance is None:
            return field(default_factory=list)
        return instance.__dict__[self.name]

    def __set__(self, instance, value: list[int | str] | str | int | None) -> None:
        if isinstance(value, list):
            instance.__dict__[self.name] = [str(item) for item in value]
        elif value is not None:
            instance.__dict__[self.name] = [str(value)]
        else:
            instance.__dict__[self.name] = []


# @TODO: NonEmptyList


class SoftFail(_DescriptorBase[bool | list[ExitStatus]]):
    """
    A descriptor for Buildkite's "soft-fail" type.
    """

    # @TODO: Coerce all 0s to `False` so `if soft_fail` is legit even in the case of a list
    # @TEST/@TODO: Deduplicate and sort.
    # @TODO: Handle `list[ExitStatus]`?
    def __set__(
        self, instance, value: bool | Literal["true", "false"] | list[int] | None
    ) -> None:
        if value in (True, "true"):
            instance.__dict__[self.name] = True
        elif value in (False, "false", None):
            instance.__dict__[self.name] = False
        elif value == []:
            instance.__dict__[self.name] = False
        elif any(status.exit_status == "*" for status in value):
            instance.__dict__[self.name] = True
        else:
            instance.__dict__[self.name] = [
                ExitStatus(exit_status=status) for status in value
            ]
