import dataclasses
from typing import Any, Callable, TypeVar, overload

T = TypeVar("T")


@overload
def field(
    *,
    default: T,
    converter: Callable[[Any], T] | None = None,
    json_loader: Callable | None = None,
    json_dumper: Callable | None = None,
    json_alias: str | None = None,
) -> T: ...


@overload
def field(
    *,
    default_factory: Callable[[], T],
    converter: Callable[[Any], T] | None = None,
    json_loader: Callable | None = None,
    json_dumper: Callable | None = None,
    json_alias: str | None = None,
) -> T: ...


@overload
def field(
    *,
    converter: Callable[[Any], T],
    json_loader: Callable | None = None,
    json_dumper: Callable | None = None,
    json_alias: str | None = None,
) -> Any: ...


def field(
    *, default=dataclasses.MISSING, default_factory=dataclasses.MISSING, **metadata
) -> Any:
    return dataclasses.field(
        default=default, default_factory=default_factory, metadata=metadata
    )  # type: ignore
