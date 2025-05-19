from pytest import param

from shimbboleth.buildkite.pipeline_config.tests.bases._base import DefaultTestBase
from shimbboleth.buildkite.pipeline_config.tests.bases.field import FieldTest


class BKStrListTest(FieldTest):
    DEFUALT = []

    PARAMETRIZATIONS = [
        param("string", ["string"], id="string"),
        param(["string1", "string2"], ["string1", "string2"], id="list"),
        param("", [""], id="empty_string"),
        param([], [], id="empty_list"),
        param(None, [], id="none"),
        # NB: Buildkite stringifies ints (presumably because YAML sucks)
        param(1, ["1"], id="int"),
        param([1, 2], ["1", "2"], id="int_list"),
        param([1, "2", 3], ["1", "2", "3"], id="mixed_list"),
    ]

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls.INVALID_STEPS += [
            # @TODO: empty dict vs nonempty_dict
            param({cls.ATTR_NAME: {"key": 1}, "type": cls.TYPENAME}, id="dict"),
        ]


class BKStrListDefaultTest(DefaultTestBase):
    DEFAULT = []

    def test__model_dump(self):
        assert self.FIELD_NAME not in self.model_load().model_dump()
        assert self.FIELD_NAME not in self.model_load({self.FIELD_NAME: []}).model_dump()
        assert (
            self.FIELD_NAME not in self.model_load({self.FIELD_NAME: None}).model_dump()
        )
        assert self.FIELD_NAME in self.model_load({self.FIELD_NAME: ["a"]}).model_dump()
