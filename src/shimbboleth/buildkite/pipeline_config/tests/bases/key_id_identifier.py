import pytest
from pytest import param

from shimbboleth.buildkite.pipeline_config.tests.bases.schema import SchemaTest


class KeyIDIdentifierTest(SchemaTest):
    PARAMETRIZATIONS = [
        #param({"key": "key"}, "key", id="key"),
        #param({"key": "key", "id": "id"}, "key", id="key_id"),
        #param({"key": "key", "id": "id", "identifier": "identifier"}, "key", id="key_id_identifier"),
        #param({"id": "id"}, "id", id="id"),
        param({"id": "id", "identifier": "identifier"}, "identifier", id="id_identifier"),
        # param({"identifier": "identifier"}, "identifier", id="identifier"),
    ]

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        if hasattr(cls, "TYPENAME"):
            cls.VALID_STEPS = [
                param({**case.values[0], "type": cls.TYPENAME}, id=case.id)
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
        instance = self.ctor(**value)
        assert instance.key == instance.id == instance.identifier == expected

    def test__setter__key(self):
        instance = self.ctor()
        instance.key = "key"
        assert instance.key == instance.id == instance.identifier == "key"

    def test__setter__id(self):
        instance = self.ctor()
        instance.id = "id"
        assert instance.key == instance.id == instance.identifier == "id"

    def test__setter__identifier(self):
        instance = self.ctor()
        instance.identifier = "identifier"
        assert instance.key == instance.id == instance.identifier == "identifier"

    # NB: Parameterized in `pytest_generate_tests`
    def test__json_load(self, value, expected):
        instance = self.model_load(value)
        assert instance.key == instance.id == instance.identifier == expected
