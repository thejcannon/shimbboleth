"""
Module defining the `Model` base class for all shimbboleth modeling.
"""

from typing import Any, Self, TypeVar, Callable, ClassVar
import dataclasses

from shimbboleth.internal.clay.jsonT import JSON, JSONObject
from shimbboleth.internal.clay.model._meta import ModelMeta


T = TypeVar("T")


class _ModelBase:
    _extra: dict[str, JSON]
    """
    If `extra` is `True`, then this contains any extra fields provided when loading.
    """


class Model(_ModelBase, metaclass=ModelMeta):
    __dataclass_fields__: ClassVar[dict[str, dataclasses.Field[Any]]]

    @classmethod
    def _json_loader_(
        cls, fieldname: str, *, json_schema_type=None
    ) -> Callable[[T], T]:
        field = cls.__dataclass_fields__[fieldname]

        assert isinstance(field, dataclasses.Field), "Did you forget to = field(...)?"
        assert (
            "json_loader" not in field.metadata
        ), f"Only one loader per field. Already: {field.metadata['json_loader']}"

        def decorator(func: T) -> T:
            # NB: `metadata` is immutable, so copy/reassign
            field.metadata = type(field.metadata)(
                field.metadata
                | {
                    "json_loader": func,
                    "json_schema_type": func.__annotations__["value"]
                    if json_schema_type is None
                    else func.__annotations__["return"]
                    if json_schema_type == "return"
                    else json_schema_type,
                }
            )
            return func

        return decorator

    @classmethod
    def _json_dumper_(cls, fieldname: str) -> Callable[[T], T]:
        field = cls.__dataclass_fields__[fieldname]
        assert isinstance(field, dataclasses.Field), "Did you forget to = field(...)?"
        assert (
            "json_dumper" not in field.metadata
        ), f"Only one dumper per field. Already: {field.metadata['json_dumper']}"

        def decorator(func: T) -> T:
            # NB: `metadata` is immutable, so copy/reassign
            field.metadata = type(field.metadata)(
                field.metadata | {"json_dumper": func}
            )
            return func

        return decorator

    @classmethod
    def model_load(cls: type[Self], value: JSONObject) -> Self:
        from shimbboleth.internal.clay.json_load import load_model

        return load_model(cls, value)

    def model_dump(self) -> JSONObject:
        from shimbboleth.internal.clay.json_dump import dump_model

        return dump_model(self)

    def __setattr__(self, name: str, value: Any):
        return super().__setattr__(name, value)
