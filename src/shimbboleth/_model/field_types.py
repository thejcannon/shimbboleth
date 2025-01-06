from dataclasses import dataclass
import re
from typing import Annotated, TypeVar, Generic, Literal

T = TypeVar("T")

NonEmpty = object()


@dataclass(frozen=True, slots=True)
class Description:
    description: str


@dataclass(frozen=True, slots=True)
class Examples:
    examples: list

    def __init__(self, *examples):
        object.__setattr__(self, "examples", list(examples))


@dataclass(frozen=True, slots=True)
class MatchesRegex:
    regex: re.Pattern

    def __init__(self, regex: str):
        object.__setattr__(self, "regex", re.compile(regex))


@dataclass(frozen=True, slots=True)
class Ge:
    bound: int


@dataclass(frozen=True, slots=True)
class Le:
    bound: int


# NB: Ne(...) is just `Not[Literal[...]]


@dataclass(frozen=True, slots=True)
class Not(Generic[T]):
    # @TODO: T can't be literal or another valid _type_
    inner: T

    def __class_getitem__(cls, key):
        return Not(key)


NonEmptyList = Annotated[list[T], NonEmpty]
NonEmptyString = Annotated[str, NonEmpty]
