from typing import Literal, Annotated, TypeAlias, Union

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
