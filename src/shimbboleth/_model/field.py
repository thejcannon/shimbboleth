from typing import Callable, Any, TypeVar, overload
import dataclasses

T = TypeVar("T")


@overload
def field(
    *,
    default: T,
    json_loader: Callable | None = None,
    json_dumper: Callable | None = None,
    json_default: Any = dataclasses.MISSING,
    json_alias: str | None = None,
    **field_kwargs,
) -> T: ...


@overload
def field(
    *,
    json_loader: Callable | None = None,
    json_dumper: Callable | None = None,
    json_default: Any = dataclasses.MISSING,
    json_alias: str | None = None,
    **field_kwargs,
) -> Any: ...


def field(
    *,
    json_loader: Callable | None = None,
    json_dumper: Callable | None = None,
    json_default: Any = dataclasses.MISSING,
    json_alias: str | None = None,
    **field_kwargs,
) -> Any:
    # @TODO Validate json default matches python default post-conversion?
    metadata = {}
    if json_loader:
        metadata["json_loader"] = json_loader
    if json_dumper:
        metadata["json_dumper"] = json_dumper
    if json_default is not dataclasses.MISSING:
        metadata["json_default"] = json_default
    if json_alias:
        metadata["json_alias"] = json_alias

    # @TODO: If the default is mutable, replace it with `default_factory: deepcopy.copy(default)` or something?

    return dataclasses.field(**field_kwargs, metadata=metadata)
