import pytest

from shimbboleth.buildkite.pipeline_config.tests.bases._base import FieldTestBase
from shimbboleth.buildkite.pipeline_config.tests.bases.schema import SchemaTest


class FieldTest(FieldTestBase, SchemaTest):
    """
    A base class that tests all the way a field can get a value.
    """
    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        if hasattr(cls, "TYPENAME"):
            cls.VALID_STEPS = [
                pytest.param({cls.FIELD_NAME: case.values[0], "type": cls.TYPENAME}, id=case.id)
                for case in cls.PARAMETRIZATIONS
            ]
            cls.INVALID_STEPS = getattr(cls, "INVALID_STEPS", []).copy()

    @classmethod
    def pytest_generate_tests(cls, metafunc: pytest.Metafunc) -> None:
        super().pytest_generate_tests(metafunc)
        parameters = metafunc.function.__code__.co_varnames
        if "value" in parameters and "expected" in parameters:
            metafunc.parametrize("value, expected", cls.PARAMETRIZATIONS)

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
        instance = self.model_load({self.FIELD_NAME: value})
        assert getattr(instance, self.ATTR_NAME) == expected
