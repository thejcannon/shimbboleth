import pytest

from shimbboleth.buildkite.pipeline_config.tests.bases.schema import SchemaTestBase
from shimbboleth.buildkite.pipeline_config.tests.bases._base import (
    DefaultTestBase,
    FieldTestBase,
)
from pytest import param


class BKStrTest(FieldTestBase, SchemaTestBase):
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

    @classmethod
    def pytest_generate_tests(cls, metafunc: pytest.Metafunc) -> None:
        super().pytest_generate_tests(metafunc)
        name = metafunc.function.__name__
        if name in BKStrTest.__dict__:
            metafunc.parametrize("value, expected", cls.PARAMETRIZATIONS)

    # NB: Parameterized in `pytest_generate_tests`
    def test__python_ctor(self, value, expected):
        instance = self.ctor(**{self.ATTR_NAME: value})
        assert getattr(instance, self.ATTR_NAME) == expected

    # NB: Parameterized in `pytest_generate_tests`
    def test__setter(self, value, expected):
        wait_step = self.ctor()
        setattr(wait_step, self.ATTR_NAME, value)
        assert getattr(wait_step, self.ATTR_NAME) == expected

    # NB: Parameterized in `pytest_generate_tests`
    def test__json_load(self, value, expected):
        instance = self.model_load({self.ATTR_NAME: value})
        assert getattr(instance, self.ATTR_NAME) == expected


class BKStrDefaultTest(DefaultTestBase):
    def test__model_dump(self):
        assert self.ATTR_NAME not in self.model_load().model_dump()
        assert (
            self.ATTR_NAME
            not in self.model_load({self.ATTR_NAME: self.DEFAULT}).model_dump()
        )
        a_string = "string"
        assert (
            self.model_load({self.ATTR_NAME: a_string}).model_dump()[self.ATTR_NAME]
            == a_string
        )
