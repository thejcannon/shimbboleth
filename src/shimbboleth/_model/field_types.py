from dataclasses import dataclass
import re

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


# TODO: Instead of `Annotated[..., NonEmpty]`, what about 'NonEmptyList' and 'NonEmptyString'?

# @TODO: add `Not[]`, UUID, Pattern
