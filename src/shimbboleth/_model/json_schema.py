from functools import singledispatch
from typing import Any, TypeVar, cast, TYPE_CHECKING
from types import UnionType, GenericAlias
import re
import uuid
import dataclasses
import logging

from shimbboleth._model.model_meta import ModelMeta
from shimbboleth._model.model import Model
from shimbboleth._model._types import AnnotationType, LiteralType, GenericUnionType
from shimbboleth._model.validation import (
    MatchesRegex,
    _NotGenericAlias,
    NonEmpty,
    Ge,
    Le,
    Not,
)

T = TypeVar("T")
ModelT = TypeVar("ModelT", bound=Model)



@singledispatch
def schema(field_type, *, model_defs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if field_type is bool:
        return {"type": "boolean"}
    if field_type is int:
        return {"type": "integer"}
    if field_type is str:
        return {"type": "string"}
    # NB: type[None] from unions (e.g. `str | None`)
    if field_type is None or field_type is type(None):
        return {"type": "null"}
    if field_type is re.Pattern:
        return {"type": "string", "format": "regex"}
    if field_type is uuid.UUID:
        return {
            "type": "string",
            "pattern": "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
        }
    if field_type is Any:
        return {}
    # NB: Dispatched manually, so we can avoid ciruclar definition with `Model.model_load`
    if isinstance(field_type, ModelMeta):
        schema_model(field_type, model_defs=model_defs)
        return {"$ref": f"#/$defs/{field_type.__name__}"}

    raise NotImplementedError(f"Schema generation for {field_type} is not implemented")


@schema.register
def schema_generic_alias(field_type: GenericAlias, *, model_defs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    container_t = field_type.__origin__
    if container_t is list:
        return schema_list(field_type=field_type, model_defs=model_defs)
    if container_t is dict:
        return schema_dict(field_type=field_type, model_defs=model_defs)
    assert False


@schema.register
def schema_union_type(field_type: UnionType, *, model_defs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {"oneOf": [schema(argT, model_defs=model_defs) for argT in field_type.__args__]}


@schema.register
def _schema_generic_union_type(field_type: GenericUnionType, *, model_defs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return schema_union_type(field_type, model_defs=model_defs)


@schema.register
def schema_literal(field_type: LiteralType,  *, model_defs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {"enum": list(field_type.__args__)}


def _schema_annotation_type(annotation: Any) -> dict[str, Any]:
    if isinstance(annotation, MatchesRegex):
        return {"pattern": annotation.regex.pattern}
    elif annotation is NonEmpty:
        return {"minLength": 1}
    elif isinstance(annotation, Ge):
        return {"minimum": annotation.bound}
    elif isinstance(annotation, Le):
        return {"maximum": annotation.bound}
    elif isinstance(annotation, _NotGenericAlias):
        return {"not": _schema_annotation_type(annotation.inner)}
    else:
        raise TypeError(f"Unsupported annotation: {annotation}")

@schema.register
def schema_annotation(field_type: AnnotationType, *, model_defs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    ret = schema(field_type.__origin__, model_defs=model_defs)
    for annotation in field_type.__metadata__:
        ret.update(_schema_annotation_type(annotation))
    return ret


def schema_list(field_type: GenericAlias, *, model_defs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    (argT,) = field_type.__args__
    return {"type": "array", "items": schema(argT, model_defs=model_defs)}


def schema_dict(field_type: GenericAlias, *, model_defs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    keyT, valueT = field_type.__args__
    key_schema = schema(keyT, model_defs=model_defs)
    assert key_schema.pop("type") == "string"
    return {
        "type": "object",
        "additionalProperties": schema(valueT, model_defs=model_defs) if valueT is not Any else True,
        **({"propertyNames": key_schema} if key_schema else {}),
    }


class _ModelFieldSchemaHelper:
    @staticmethod
    def _get_field_type_schema(field: dataclasses.Field, *, model_defs: dict[str, dict[str, Any]]) -> dict[str, Any]:
        json_loader = field.metadata.get("json_loader", None)
        if json_loader:
            input_type = getattr(
                json_loader, "json_schema_type", json_loader.__annotations__["value"]
            )
            output_type = json_loader.__annotations__["return"]
            assert (
                output_type == field.type
            ), f"for {json_loader} {output_type=} {field.type=}"
            return schema(input_type, model_defs=model_defs)
        return schema(field.type, model_defs=model_defs)

    @staticmethod
    def visit_model_field(field: dataclasses.Field, *, model_defs: dict[str, dict[str, Any]]) -> dict[str, Any]:
        field_schema = _ModelFieldSchemaHelper._get_field_type_schema(field, model_defs=model_defs)
        if field.default is not dataclasses.MISSING:
            field_schema["default"] = field.default
        elif field.default_factory is not dataclasses.MISSING:
            field_schema["default"] = field.default_factory()
        return field_schema

def schema_model(model_type: type[ModelT], *, model_defs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    model_name = model_type.__name__
    if model_name not in model_defs:
        fields = tuple(field for field in dataclasses.fields(model_type) if field.init)
        model_defs[model_name]  = {
            "type": "object",
            "properties": {
                **{field.name: _ModelFieldSchemaHelper.visit_model_field(field, model_defs=model_defs) for field in fields},
                **{
                    name: {"$ref": f"#/$defs/{model_name}/properties/{field_alias.alias_of}"}
                    for name, field_alias in model_type.__field_aliases__.items()
                },
            },
            "required": [
                field.name
                for field in fields
                if (
                    field.default is dataclasses.MISSING
                    and field.default_factory is dataclasses.MISSING
                )
            ],
            "additionalProperties": model_type.__allow_extra_properties__,
        }

    return {"$ref": f"#/$defs/{model_name}"}
