import pytest
from pytest import param

from shimbboleth.buildkite.pipeline_config.tests.bases.schema import SchemaTestBase
from shimbboleth.buildkite.pipeline_config.tests.bases._base import FieldTestBase

parameterize_bk_str_list = pytest.mark.parametrize(
    "value, expected",
    [
        param("string", ["string"], id="string"),
        param(["string1", "string2"], ["string1", "string2"], id="list"),
        param("", [""], id="empty_string"),
        param([], [], id="empty_list"),
        param(None, [], id="none"),
        # NB: Buildkite stringifies ints (presumably because YAML sucks)
        param(1, "1", id="int"),
        param([1, 2], ["1", "2"], id="int_list"),
    ],
)


class BKStrListTestBase(FieldTestBase, SchemaTestBase):
    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls.VALID_STEPS += [
            param({cls.ATTR_NAME: case.values[0], "type": cls.TYPENAME}, id=case.id)
            for case in parameterize_bk_str_list.args[1]
        ]
        cls.INVALID_STEPS += [
            param({cls.ATTR_NAME: {"key": 1}, "type": cls.TYPENAME}, id="dict"),
        ]

    def test__model_dump(self):
        assert self.ATTR_NAME not in self.model_load().model_dump()
        assert self.ATTR_NAME not in self.model_load({self.ATTR_NAME: []}).model_dump()
        assert (
            self.ATTR_NAME not in self.model_load({self.ATTR_NAME: None}).model_dump()
        )
        assert self.ATTR_NAME in self.model_load({self.ATTR_NAME: ["a"]}).model_dump()

    @parameterize_bk_str_list
    def test__python_ctor(self, value, expected):
        instance = self.ctor(**{self.ATTR_NAME: value})
        assert getattr(instance, self.ATTR_NAME) == expected

    @parameterize_bk_str_list
    def test__setter(self, value, expected):
        instance = self.ctor()
        setattr(instance, self.ATTR_NAME, value)
        assert getattr(instance, self.ATTR_NAME) == expected

    @parameterize_bk_str_list
    def test__json_load(self, value, expected):
        instance = self.model_load({self.ATTR_NAME: value})
        assert getattr(instance, self.ATTR_NAME) == expected
