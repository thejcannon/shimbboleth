import pytest

from shimbboleth.buildkite.pipeline_config.tests.bases._base import FieldTestBase

parameterize_bk_bools = pytest.mark.parametrize(
    "value, expected",
    [
        pytest.param(True, True, id="True"),
        pytest.param("true", True, id="'true'"),
        pytest.param(False, False, id="False"),
        pytest.param("false", False, id="'false'"),
        # @TODO: Should `None` instead be the default?
        pytest.param(None, False, id="None"),
    ],
)


class BKBoolTest(FieldTestBase[bool]):
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

    @parameterize_bk_bools
    def test__python_ctor(self, value, expected):
        instance = self.ctor(**{self.ATTR_NAME: value})
        assert getattr(instance, self.ATTR_NAME) is expected

    @parameterize_bk_bools
    def test__setter(self, value, expected):
        wait_step = self.ctor()
        setattr(wait_step, self.ATTR_NAME, value)
        assert getattr(wait_step, self.ATTR_NAME) is expected

    @parameterize_bk_bools
    def test__json_load(self, value, expected):
        instance = self.model_load({self.ATTR_NAME: value})
        assert getattr(instance, self.ATTR_NAME) is expected

    # @TODO: Add schema valid/invalid tests
