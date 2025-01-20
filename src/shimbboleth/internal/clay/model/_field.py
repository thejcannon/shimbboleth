from typing import Any, TypeVar, Callable
import dataclasses
from typing import overload



T = TypeVar("T")


@overload
def field(
    *,
    default: T,
    json_loader: Callable | None = None,
    json_dumper: Callable | None = None,
    json_alias: str | None = None,
) -> T: ...

@overload
def field(
    *,
    default_factory: Callable[[], T],
    json_loader: Callable | None = None,
    json_dumper: Callable | None = None,
    json_alias: str | None = None,
) -> T: ...

@overload
def field(
    *,
    json_loader: Callable | None = None,
    json_dumper: Callable | None = None,
    json_alias: str | None = None,
) -> Any: ...


def field(*, default = dataclasses.MISSING, default_factory = dataclasses.MISSING, **metadata) -> Any:
    return dataclasses.field(default=default, default_factory=default_factory, metadata=metadata)  # type: ignore
