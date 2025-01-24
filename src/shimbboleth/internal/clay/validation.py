"""
Validation of model fields.

NOTE: This only handles Annotated validations (E.g. `Annotated[int, Ge(10)]`)
"""

from typing import TypeVar, ClassVar, Annotated, Protocol, overload
import dataclasses
from contextlib import contextmanager
import re

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


class Validator(Protocol):
    def __call__(self, value) -> None: ...


class ValidationError(ValueError):
    @overload
    def __init__(self, value, *, expectation: str, qualifier: str = ""): ...

    @overload
    def __init__(self, value, *, expectation: str, qualifier: str = "", index: int): ...

    @overload
    def __init__(self, value, *, expectation: str, qualifier: str = "", key: str): ...

    @overload
    def __init__(self, value, *, expectation: str, qualifier: str = "", attr: str): ...

    def __init__(
        self,
        value,
        *,
        expectation: str,
        qualifier: str = "",
        index: int | None = None,
        key: str | None = None,
        attr: str | None = None,
    ):
        self.value = value
        self.expectation = expectation
        self.qualifier = qualifier
        self.path = []
        self.add_context(index=index, key=key, attr=attr)

    def __str__(self):
        qualifier = f"{self.qualifier} " if self.qualifier else ""
        return (
            f"Expected {qualifier}`{self.value!r}` to {self.expectation}"
            + "\n"
            + f"Path: {''.join(self.path)}"
        )

    def add_context(
        self,
        *,
        index: int | None = None,
        key: str | None = None,
        attr: str | None = None,
    ):
        if index is not None:
            self.path.insert(0, f"[{index}]")
        if key is not None:
            self.path.insert(0, f"[{key!r}]")
        if attr is not None:
            self.path.insert(0, f".{attr}")

    @contextmanager
    @staticmethod
    def context(
        *, index: int | None = None, key: str | None = None, attr: str | None = None
    ):
        try:
            yield
        except ValidationError as e:
            e.add_context(index=index, key=key, attr=attr)
            raise


class _NonEmptyT(Validator):
    description: ClassVar[str] = "not be empty"

    def __call__(self, value: str | dict | list):
        if len(value) == 0:
            raise ValidationError(value, expectation="be non-empty")

    def __repr__(self) -> str:
        return "NonEmpty"


NonEmpty = _NonEmptyT()
NonEmptyString = Annotated[str, NonEmpty]
NonEmptyList = Annotated[list[T], NonEmpty]
NonEmptyDict = Annotated[dict[K, V], NonEmpty]


@dataclasses.dataclass(frozen=True, slots=True)
class MatchesRegex(Validator):
    regex: re.Pattern

    def __init__(self, regex: str):
        object.__setattr__(self, "regex", re.compile(regex))

    def __call__(self, value: str):
        if not self.regex.fullmatch(value):
            raise ValidationError(value, expectation=self.expectation)

    @property
    def expectation(self) -> str:
        return f"match regex `{self.regex.pattern}`"


@dataclasses.dataclass(frozen=True, slots=True)
class MaxLength:
    limit: int

    def __call__(self, value: dict):
        if len(value) > self.limit:
            raise ValidationError(value, expectation=self.expectation)

    @property
    def expectation(self) -> str:
        return f"have a length less than `{self.limit}`"


SingleKeyDict = Annotated[dict[K, V], MaxLength(1)]


@dataclasses.dataclass(frozen=True, slots=True)
class _NotGenericAlias:
    inner: type

    def __repr__(self):
        return f"Not[{self.inner!r}]"


@dataclasses.dataclass(frozen=True, slots=True)
class Not(Validator):
    validators: list[Validator]

    def __class_getitem__(cls, inner: type):
        return _NotGenericAlias(inner)

    def __call__(self, value):
        for validator in self.validators:
            try:
                validator(value)
            except ValidationError:
                pass
            else:
                expectation = validator.expectation  # type: ignore
                raise ValidationError(value, expectation=f"not {expectation}")


@dataclasses.dataclass(frozen=True, slots=True)
class Ge(Validator):
    bound: int

    def __call__(self, value: int):
        if value < self.bound:
            raise ValidationError(value, expectation=self.expectation)

    @property
    def expectation(self) -> str:
        return f"be >= {self.bound}"


@dataclasses.dataclass(frozen=True, slots=True)
class Le(Validator):
    bound: int

    def __call__(self, value: int):
        if value > self.bound:
            raise ValidationError(value, expectation=self.expectation)

    @property
    def expectation(self) -> str:
        return f"be <= {self.bound}"
