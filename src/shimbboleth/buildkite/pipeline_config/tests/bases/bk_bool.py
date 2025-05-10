import pytest
from pytest import param

from shimbboleth.buildkite.pipeline_config.tests.bases._base import (
    DefaultTestBase,
    FieldTestBase,
)
from shimbboleth.buildkite.pipeline_config.tests.bases.schema import SchemaTestBase


class BKBoolTest(FieldTestBase, SchemaTestBase):
    PARAMETRIZATIONS = [
        param(True, True, id="True"),
        param("true", True, id="true"),
        param(False, False, id="False"),
        param("false", False, id="false"),
        # @TODO: Should `None` instead be the default? Or the default?
        param(None, False, id="None"),
    ]

    @classmethod
    def pytest_generate_tests(cls, metafunc: pytest.Metafunc) -> None:
        super().pytest_generate_tests(metafunc)
        name = metafunc.function.__name__
        if name in BKBoolTest.__dict__:
            metafunc.parametrize("value, expected", cls.PARAMETRIZATIONS)

    # NB: Parameterized in `pytest_generate_tests`
    def test__python_ctor(self, value, expected):
        instance = self.ctor(**{self.ATTR_NAME: value})
        assert getattr(instance, self.ATTR_NAME) is expected

    # NB: Parameterized in `pytest_generate_tests`
    def test__setter(self, value, expected):
        wait_step = self.ctor()
        setattr(wait_step, self.ATTR_NAME, value)
        assert getattr(wait_step, self.ATTR_NAME) is expected

    # NB: Parameterized in `pytest_generate_tests`
    def test__json_load(self, value, expected):
        instance = self.model_load({self.ATTR_NAME: value})
        assert getattr(instance, self.ATTR_NAME) is expected

    # @TODO: Add schema valid/invalid tests?


class BKBoolDefaultTest(DefaultTestBase):
    def test__model_dump(self):
        assert self.ATTR_NAME not in self.model_load().model_dump()
        assert (
            self.ATTR_NAME
            not in self.model_load({self.ATTR_NAME: self.DEFAULT}).model_dump()
        )
        opposite = not self.DEFAULT
        assert (
            self.model_load({self.ATTR_NAME: opposite}).model_dump()[self.ATTR_NAME]
            is opposite
        )
