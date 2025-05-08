from typing import Literal, Annotated, TypeAlias, Union, Generic, TypeVar, overload
from shimbboleth.internal.clay.jsonT import JSONObject

AnnotationType: TypeAlias = type(Annotated[None, None])  # type: ignore
"""The "type" of an Annotated type. E.g. return type of `Annotated.__class_getitem__`."""

LiteralType: TypeAlias = type(Literal[None])  # type: ignore
"""The "type" of a Literal type. E.g. return type of `Literal.__class_getitem__`"""

GenericUnionType: TypeAlias = type(Union[int, str])  # type: ignore
"""The "type" of a Union type. This differs from types.UnionType (which is returned by `int | str`)."""


# NB: Differs from `typing.get_origin`. This one doesn't special-case `Annotated`.
def get_origin(t, /):
    ret = t
    while hasattr(ret, "__origin__"):
        ret = ret.__origin__
    return ret


T = TypeVar("T")


class NonEmptyList(Generic[T]):
    @classmethod
    def __shimbboleth_json_schema__(cls, *, model_defs: dict[str, JSONObject]) -> JSONObject:
        return {"type": "array", "minItems": 1}

    def __set_name__(self, owner, name: str) -> None:
        self.name = name

    @overload
    def __get__(self, instance: None, owner) -> None: ...

    @overload
    def __get__(self, instance: object, owner) -> list[T]: ...

    def __get__(self, instance, owner) -> list[T]:
        if instance is None:
            return None
        return getattr(instance, self.name)

    def __set__(self, instance, value: list[T] | None) -> None:
        setattr(instance, self.name, value or [])
