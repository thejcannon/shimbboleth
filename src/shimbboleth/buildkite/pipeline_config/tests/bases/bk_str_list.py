import pytest
from pytest import param

from shimbboleth.buildkite.pipeline_config.tests.bases.schema import SchemaTestBase
from shimbboleth.buildkite.pipeline_config.tests.bases._base import FieldTestBase


class BKStrListTestBase(FieldTestBase, SchemaTestBase):
    PARAMETERIZATIONS = [
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

    @classmethod
    def pytest_generate_tests(cls, metafunc: pytest.Metafunc) -> None:
        super().pytest_generate_tests(metafunc)
        name = metafunc.function.__name__
        if name in BKStrListTestBase.__dict__ and name not in ("test__model_dump",):
            metafunc.parametrize("value, expected", cls.PARAMETERIZATIONS)

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls.VALID_STEPS += [
            param({cls.ATTR_NAME: case.values[0], "type": cls.TYPENAME}, id=case.id)
            for case in cls.PARAMETERIZATIONS
        ]
        cls.INVALID_STEPS += [
            # @TODO: empty dict vs nonempty_dict
            param({cls.ATTR_NAME: {"key": 1}, "type": cls.TYPENAME}, id="dict"),
        ]

    def test__model_dump(self):
        assert self.ATTR_NAME not in self.model_load().model_dump()
        assert self.ATTR_NAME not in self.model_load({self.ATTR_NAME: []}).model_dump()
        assert (
            self.ATTR_NAME not in self.model_load({self.ATTR_NAME: None}).model_dump()
        )
        assert self.ATTR_NAME in self.model_load({self.ATTR_NAME: ["a"]}).model_dump()


    # NB: Parameterized in `pytest_generate_tests`
    def test__python_ctor(self, value, expected):
        instance = self.ctor(**{self.ATTR_NAME: value})
        assert getattr(instance, self.ATTR_NAME) == expected

    # NB: Parameterized in `pytest_generate_tests`
    def test__setter(self, value, expected):
        instance = self.ctor()
        setattr(instance, self.ATTR_NAME, value)
        assert getattr(instance, self.ATTR_NAME) == expected


    # NB: Parameterized in `pytest_generate_tests`
    def test__json_load(self, value, expected):
        instance = self.model_load({self.ATTR_NAME: value})
        assert getattr(instance, self.ATTR_NAME) == expected
