import pytest

from shimbboleth.buildkite.pipeline_config.tests.bases.schema import SchemaTest
from shimbboleth.buildkite.pipeline_config.tests.bases._base import (
    DefaultTestBase,
    FieldTest,
)
from pytest import param


class BKStrTest(FieldTest):
    PARAMETRIZATIONS = [
        param(None, None, id="none"),
        param("", "", id="empty_string"),
        param("string", "string", id="string"),
        # NB: Buildkite treats Falsey values as `None`/`""`/not-given
        param([], None, id="empty_list"),
        param({}, None, id="empty_dict"),
        # NB: Buildkite stringifies ints
        param(1, "1", id="int"),
    ]

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls.INVALID_STEPS += [
            param({cls.ATTR_NAME: [1], "type": cls.TYPENAME}, id="int_list"),
            param(
                {cls.ATTR_NAME: {"test-key": "value"}, "type": cls.TYPENAME},
                id="non_empty_dict",
            ),
            # NB: Buildkite doesn't stringify floats
            param({cls.ATTR_NAME: 1.234, "type": cls.TYPENAME}, id="float"),
        ]

class BKStrDefaultTest(DefaultTestBase):
    def test__model_dump(self):
        assert self.FIELD_NAME not in self.model_load().model_dump()
        assert (
            self.FIELD_NAME
            not in self.model_load({self.FIELD_NAME: self.DEFAULT}).model_dump()
        )
        a_string = "string"
        assert (
            self.model_load({self.FIELD_NAME: a_string}).model_dump()[self.FIELD_NAME]
            == a_string
        )
