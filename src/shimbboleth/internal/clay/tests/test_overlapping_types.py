"""
Test the places/ways we forbid overlapping types in unions.

This is because in more than one place we have logic that tries to map
an object's tyoe to a type in a union, and so making overlapping forbidden
simplifies that logic.
"""

from typing import Annotated, Union

from shimbboleth.internal.clay.model import Model

import pytest
from pytest import param


class Other1(Model):
    pass


class Other2(Model):
    pass


@pytest.mark.parametrize(
    "fieldT",
    [
        param(int | Annotated[int, ""], id="bare-and-annotated"),
        param(list[str] | list[int], id="two-lists"),
        param(dict[str, str] | Other1, id="dict-and-model"),
        param(Other1 | Other2, id="dict-and-model"),
        param(int | (str | None | Annotated[int, ""]), id="nested-union"),
    ],
)
class Test_Overlapping:
    def test_model_field(self, fieldT):
        with pytest.raises(Exception, match="unsupported"):
            type(
                "MyModel", (Model,), {"__annotations__": {"field": fieldT}}
            ).model_load({"field": None})

    def test_json_loader(self, fieldT):
        class MyModel(Model):
            field: None

        @MyModel._json_loader_("field")
        def load_field(value: None) -> None:
            pass

        load_field.__annotations__["value"] = fieldT

        with pytest.raises(Exception, match="unsupported"):
            MyModel.model_load({"field": None})


@pytest.mark.parametrize(
    "fieldT",
    [str | int | list[str | int], int | Union[int, str], Union[int, str] | int],
)
def test_not_overlapping(fieldT):
    type("MyModel", (Model,), {"__annotations__": {"field": fieldT}}).model_load(
        {"field": 0}
    )
