"""
Tests related to `json_load.py`.
"""

import pytest
from typing import Literal, Annotated, ClassVar
import uuid
from pytest import param

from shimbboleth.internal.clay.model import Model, field, FieldAlias
from shimbboleth.internal.clay.validation import MatchesRegex, NonEmpty, Ge
from shimbboleth.internal.clay.json_load import load


def make_model(attrs, **kwargs):
    return type(Model)("MyModel", (Model,), attrs, **kwargs)


def str_to_int(value: str) -> int:
    return int(value)


@pytest.mark.parametrize(
    ("field_type", "data"),
    [
        param(bool, True, id="simple"),
        param(bool, False, id="simple"),
        param(int, 0, id="simple"),
        param(int, 1, id="simple"),
        param(str, "a string", id="simple"),
        param(str, "", id="simple"),
        param(None, None, id="simple"),
        # dict
        param(dict[str, int], {}, id="dict"),
        param(dict[str, int], {"key": 0}, id="dict"),
        param(dict[str, int], {"key1": 0, "key2": 1}, id="dict"),
        param(Annotated[dict[str, int], NonEmpty], {"key": 0}, id="dict"),
        param(Annotated[dict[str, int], NonEmpty], {"": 0}, id="dict"),
        param(
            Annotated[dict[Annotated[str, NonEmpty], int], NonEmpty],
            {"key": 0},
            id="dict",
        ),
        # list
        param(list[int], [], id="list"),
        param(list[int], [1, 2, 3], id="list"),
        param(list[str], ["a", "b", "c"], id="list"),
        param(list[bool], [True, False], id="list"),
        param(list[Annotated[str, NonEmpty]], [""], id="list"),
        param(Annotated[list[str], NonEmpty], [], id="list"),
        # literal
        param(Literal["a", "b", "c"], "a", id="literal"),
        param(Literal["a", "b", "c"], "b", id="literal"),
        param(Literal["a", "b", "c"], "c", id="literal"),
        param(Literal[1, 2, 3], 1, id="literal"),
        param(Literal[1, 2, 3], 2, id="literal"),
        param(Literal[1, 2, 3], 3, id="literal"),
        # union
        param(int | str, 42, id="union"),
        param(int | str, "hello", id="union"),
        param(bool | str, True, id="union"),
        param(bool | str, "true", id="union"),
        param(list[str] | dict[str, int], ["1", "2", "3"], id="union"),
        param(list[str] | dict[str, int], {"a": 1, "b": 2}, id="union"),
        # misc
        param(Annotated[str, MatchesRegex(r"^.*$")], "", id="annotated"),
    ],
)
def test_no_change(field_type, data):
    """Test loading with types+objects that are loaded as themselves"""
    assert load(field_type, data=data) == data


@pytest.mark.parametrize(
    ("field_type", "data"),
    [
        param(uuid.UUID, "123e4567-e89b-12d3-a456-426614174000", id="uuid"),
        param(uuid.UUID, "550e8400-e29b-41d4-a716-446655440000", id="uuid"),
    ],
)
def test_passing_uuid(field_type, data):
    assert load(field_type, data=data) == uuid.UUID(data)


@pytest.mark.parametrize(
    ("field_type", "data"),
    [
        param(bool, 0, id="simple"),
        param(bool, None, id="simple"),
        param(int, True, id="simple"),
        param(int, False, id="simple"),
        # dict
        param(dict[str, int], [], id="dict"),
        param(dict[str, int], {0: 0}, id="dict"),
        param(dict[str, int], {0: None}, id="dict"),
        param(dict[str, int], {"key": False}, id="dict"),
        param(dict[str, bool], {"key": 1}, id="dict"),
        param(dict[str, int], {"key1": 0, "key2": "value"}, id="dict"),
        # list
        param(list[int], dict(), id="list"),
        param(list[int], [1, "2", 3], id="list"),
        param(list[str], ["a", 1, "c"], id="list"),
        param(list[int], [True], id="list"),
        param(list[bool], [True, "False"], id="list"),
        param(list[bool], [0], id="list"),
        param(list[int], "not a list", id="list"),
        # uuid
        param(uuid.UUID, "not-a-uuid", id="uuid"),
        param(uuid.UUID, 123, id="uuid"),
        param(uuid.UUID, True, id="uuid"),
        # literal
        param(Literal["a", "b", "c"], "d", id="literal"),
        param(Literal["a", "b", "c"], 1, id="literal"),
        param(Literal[True], 1, id="literal"),
        param(Literal[1], True, id="literal"),
        param(Literal[False], 0, id="literal"),
        param(Literal[0], False, id="literal"),
        # union
        param(int | str, True, id="union"),
        param(int | str, [], id="union"),
        param(bool | str, 0, id="union"),
        param(bool | int, "string", id="union"),
        param(list[str] | dict[str, int], set(), id="union"),
        param(list[str] | dict[str, int], "string", id="union"),
    ],
)
def test_invalid(field_type, data):
    """Test invalid combinations of type + object"""
    with pytest.raises(TypeError):
        load(field_type, data=data)


@pytest.mark.parametrize(
    ("model_def", "data", "expected"),
    [
        (
            make_model(
                {},
                extra=True,
            ),
            {"field": 0},
            {},
        ),
        (
            make_model(
                {
                    "__annotations__": {"field": int},
                    "field": 0,
                },
            ),
            {},
            {"field": 0},
        ),
        (
            make_model(
                {
                    "__annotations__": {"field": int},
                    "field": field(default=0),
                },
            ),
            {},
            {"field": 0},
        ),
        (
            make_model(
                {
                    "__annotations__": {"field": int},
                },
            ),
            {"field": 0},
            {"field": 0},
        ),
        (
            make_model(
                {
                    "__annotations__": {"field": int},
                    "field": field(json_loader=str_to_int),
                },
            ),
            {"field": "42"},
            {"field": 42},
        ),
    ],
)
def test_model(model_def, data, expected):
    assert load(model_def, data=data) == model_def(**expected)


@pytest.mark.parametrize(
    ("model_def", "data"),
    [
        (
            make_model(
                {},
                extra=False,
            ),
            {"field": 0},
        ),
        (
            make_model(
                {
                    "__annotations__": {"field": int},
                },
            ),
            {},
        ),
        (
            make_model(
                {
                    "__annotations__": {"field": int},
                },
            ),
            {"field": True},
        ),
        (
            make_model(
                {
                    "__annotations__": {"field": int},
                    "field": field(json_loader=str_to_int),
                },
            ),
            {"field": 0},
        ),
    ],
)
def test_model__invalid(model_def, data):
    with pytest.raises(TypeError):
        load(model_def, data=data)


def test_model__extras():
    class ModelWithExtras(Model, extra=True):
        pass

    instance = load(ModelWithExtras, data={"field": "value"})
    assert instance._extra["field"] == "value"

    class ModelWithoutExtras(Model, extra=False):
        pass

    instance = load(ModelWithoutExtras, data={})
    assert instance._extra == {}


def test_model_in_other_type():
    class MyModel(Model):
        field: str

    assert load(list[MyModel], data=[{"field": "one king mop"}]) == [
        MyModel(field="one king mop")
    ]
    assert load(dict[str, MyModel], data={"key": {"field": "one king mop"}}) == {
        "key": MyModel(field="one king mop")
    }
    assert load(MyModel | None, data=None) is None


def test_field_alias():
    class MyModel(Model):
        field: str
        alias: ClassVar = FieldAlias("field")

    instance = load(MyModel, data={"alias": "value"})
    assert instance.field == "value"


def test_json_alias():
    class MyModel(Model):
        if_condition: str = field(json_alias="if")

    assert load(MyModel, data={"if": "value"}).if_condition == "value"

    with pytest.raises(TypeError):
        load(MyModel, data={"if_condition": "value"})


def test__load_error__json_alias_path():
    """
    Test when loading fails the path in the error uses the `json_alias`.
    """

    class MyModel(Model):
        integer: int = field(json_alias="int")

    with pytest.raises(Exception, match=r"Path: .int"):
        MyModel.model_load({"int": ""})


def test__validation_error__json_alias_path():
    """
    Test when validation fails (which is Python-side)
    the path in the error uses the `json_alias`.
    """

    class MyModel(Model):
        integer: Annotated[int, Ge(0)] = field(json_alias="int")

    with pytest.raises(Exception, match=r"Path: .int"):
        MyModel.model_load({"int": -1})
