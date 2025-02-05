from contextlib import contextmanager
from functools import singledispatch
from typing import TYPE_CHECKING, Any, TypeVar
from types import UnionType, GenericAlias
import re
import copy
import uuid
import dataclasses
import logging

from shimbboleth.internal.utils import is_shimbboleth_pytesting
from shimbboleth.internal.clay.jsonT import JSONObject
from shimbboleth.internal.clay.model import Model
from shimbboleth.internal.clay._types import (
    AnnotationType,
    LiteralType,
    GenericUnionType,
    get_origin,
)
from shimbboleth.internal.clay.validation import ValidationError

T = TypeVar("T")
ModelT = TypeVar("ModelT", bound=Model)


LOG = logging.getLogger()


class JSONLoadError(ValidationError, TypeError):
    pass


class WrongTypeError(JSONLoadError):
    def __init__(self, expected, data):
        super().__init__(value=data, expectation=f"be of type `{expected}`")


class ExtrasNotAllowedError(JSONLoadError):
    def __init__(self, model_type: type[Model], extras: JSONObject):
        super().__init__(
            value=extras,
            expectation=f"not not be provided. {model_type.__name__} dosn't support extra keys.",
            qualifier="extra keys",
        )


class NotAValidUUIDError(JSONLoadError):
    def __init__(self, data):
        super().__init__(value=data, expectation="be a valid UUID")


class NotAValidPatternError(JSONLoadError):
    def __init__(self, data):
        super().__init__(value=data, expectation="be a valid regex pattern")


class MissingFieldsError(JSONLoadError):
    def __init__(self, model_name: str, *fieldnames: str):
        super().__init__(
            value=", ".join(fieldnames),
            expectation=f"be provided for model `{model_name}`",
            qualifier="required fields",
        )


def _ensure_is(data, expected: type[T]) -> T:
    if type(data) is not expected:
        raise WrongTypeError(expected.__name__, data)
    return data


@singledispatch
def load(field_type, *, data):  # type: ignore
    if field_type is bool:
        return load_bool(data)
    if field_type is int:
        return load_int(data)
    if field_type is str:
        return load_str(data)
    # NB: type[None] from unions (e.g. `str | None`)
    if field_type is None or field_type is type(None):
        return load_none(data)
    if field_type is re.Pattern:
        return load_pattern(data)
    if field_type is uuid.UUID:
        return load_uuid(data)
    if field_type is Any:
        return data
    # NB: Dispatched manually, so we can avoid ciruclar definition with `Model.model_load`
    if issubclass(field_type, Model):
        return field_type.model_load(data)

    raise WrongTypeError(field_type, data)


@load.register
def load_generic_alias(field_type: GenericAlias, *, data: Any):
    container_t = field_type.__origin__
    if container_t is list:
        return load_list(data, field_type=field_type)
    if container_t is dict:
        return load_dict(data, field_type=field_type)


def _get_jsontype(field_type) -> type:
    if isinstance(field_type, LiteralType):
        literal_types = {type(val) for val in field_type.__args__}
        if len(literal_types) > 1:
            raise TypeError(f"Literal args must all be the same type: {field_type}")
        return literal_types.pop()

    rawtype = get_origin(field_type)
    if isinstance(rawtype, type) and issubclass(rawtype, Model):
        return dict
    if rawtype is re.Pattern:
        return str
    if rawtype is uuid.UUID:
        return str

    return rawtype


@load.register
def load_union_type(field_type: UnionType, *, data: Any):
    # NB: This is safe, since we check for overlapping types in
    #  `src/shimbboleth/internal/clay/_validators.py` in `get_union_type_validators`.
    # (not true, JSON loaders)

    if is_shimbboleth_pytesting():
        jsontypes = {_get_jsontype(argT) for argT in field_type.__args__}
        assert (
            len(field_type.__args__) == len(jsontypes)
        ), f"Overlapping outer types in Union is unsupported: Input: `{field_type.__args__}`. Result: `{jsontypes}`."

    for argT in field_type.__args__:
        expected_type = _get_jsontype(argT)
        # NB: Have to use `is` instead of `isinstance` because `bool` inherits from `int`
        if type(data) is expected_type:
            return load(argT, data=data)

    raise WrongTypeError(field_type, data)


@load.register
def _load_generic_union_type(field_type: GenericUnionType, *, data: Any):
    return load_union_type(field_type, data=data)


@load.register
def load_literal(field_type: LiteralType, *, data: Any):
    for possibility in field_type.__args__:
        # NB: compare bool/int by identity (since `bool` inherits from `int`)
        if data is possibility:
            return data
        if isinstance(possibility, str) and isinstance(data, str):
            if data == possibility:
                return data

    raise WrongTypeError(field_type, data)


@load.register
def load_annotation(field_type: AnnotationType, *, data: Any):
    baseType = field_type.__origin__
    return load(baseType, data=data)


def load_bool(data: Any) -> bool:
    return _ensure_is(data, bool)


def load_str(data: Any) -> str:
    return _ensure_is(data, str)


def load_int(data: Any) -> int:
    return _ensure_is(data, int)


def load_none(data: Any) -> None:
    return _ensure_is(data, type(None))


def load_list(data: Any, *, field_type: GenericAlias) -> list:
    data = _ensure_is(data, list)
    (argT,) = field_type.__args__
    ret = []
    for index, item in enumerate(data):
        with ValidationError.context(index=index):
            ret.append(load(argT, data=item))
    return ret


def load_dict(data: Any, *, field_type: GenericAlias) -> dict:
    data = _ensure_is(data, dict)
    keyT, valueT = field_type.__args__
    ret = {}
    for key, value in data.items():
        loaded_key = load(keyT, data=key)
        with ValidationError.context(key=key):
            ret[loaded_key] = load(valueT, data=value)
    return ret


def load_pattern(data: Any) -> re.Pattern:
    data = _ensure_is(data, str)
    try:
        return re.compile(data)
    except re.error:
        raise NotAValidPatternError(data)


def load_uuid(data: Any) -> uuid.UUID:
    data = _ensure_is(data, str)
    try:
        return uuid.UUID(data)
    except ValueError:
        raise NotAValidUUIDError(data)


class _LoadModelHelper:
    @staticmethod
    def handle_field_aliases(model_type: type[Model], data: JSONObject) -> dict:
        data_copy = data
        for field_alias_name, field_alias in model_type.__field_aliases__.items():
            if field_alias_name in data:
                if data_copy is data:
                    data_copy = copy.copy(data)

                value = data_copy.pop(field_alias_name)
                if (
                    field_alias.json_mode == "prepend"
                    or data.get(field_alias.alias_of) is None
                ):
                    data_copy[field_alias.alias_of] = value

        return data_copy

    @staticmethod
    def rename_json_aliases(model_type: type[Model], data: JSONObject):
        for field in dataclasses.fields(model_type):
            if not field.init:
                continue
            json_alias = field.metadata.get("json_alias")
            if json_alias and json_alias in data:
                data[field.name] = data.pop(json_alias)

    @staticmethod
    def get_extras(model_type: type[Model], data: JSONObject) -> JSONObject:
        extras = {}
        for data_key in frozenset(data.keys()):
            if data_key not in model_type.__json_fieldnames__:
                extras[data_key] = data.pop(data_key)

        if extras and not model_type.__allow_extra_properties__:
            raise ExtrasNotAllowedError(model_type, extras)

        return extras

    @staticmethod
    def load_field(field: dataclasses.Field, data: JSONObject):
        json_loader = field.metadata.get("json_loader", None)
        expected_type: Any = (
            json_loader.__annotations__["value"] if json_loader else field.type
        )

        with ValidationError.context(attr=field.metadata.get("json_alias", field.name)):
            value = load(expected_type, data=data[field.name])
            if json_loader:
                value = json_loader(value)

        return value

    @staticmethod
    def check_required_fields(model_type: type[Model], data: JSONObject):
        missing_fields = [
            field.name
            for field in dataclasses.fields(model_type)
            if field.init
            and field.name not in data
            and field.default is dataclasses.MISSING
            and field.default_factory is dataclasses.MISSING
        ]
        if missing_fields:
            raise MissingFieldsError(model_type.__name__, *missing_fields)

    @contextmanager
    @staticmethod
    def rename_field_alias_in_path(model_type: type[Model]):
        try:
            yield
        except ValidationError as e:
            if not e.path or not e.path[-1].startswith("."):
                raise

            field = model_type.__dataclass_fields__.get(e.path[-1][1:])
            if field is not None:
                json_alias = field.metadata.get("json_alias")
                if json_alias:
                    e.path[-1] = "." + json_alias
            raise


def load_model(model_type: type[ModelT], data: JSONObject) -> ModelT:
    data = load(JSONObject, data=data)
    data = _LoadModelHelper.handle_field_aliases(model_type, data)

    extras = _LoadModelHelper.get_extras(model_type, data)
    _LoadModelHelper.rename_json_aliases(model_type, data)

    init_kwargs = {
        field.name: _LoadModelHelper.load_field(field, data)
        for field in dataclasses.fields(model_type)
        if field.name in data
    }
    _LoadModelHelper.check_required_fields(model_type, init_kwargs)

    with _LoadModelHelper.rename_field_alias_in_path(model_type):
        instance = model_type(**init_kwargs)

    instance._extra = extras
    return instance

if TYPE_CHECKING:
    def load(field_type: type[T], *, data) -> T: ...
