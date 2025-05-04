from shimbboleth.internal.clay.model import Model
from typing import ClassVar, Any
import pytest

from shimbboleth.buildkite.pipeline_config.tests.helpers import get_upstream_schema
from shimbboleth.buildkite.pipeline_config.tests.bases._base import FieldTestBase

parameterize_bk_strs = pytest.mark.parametrize(
    "value, expected",
    [
        pytest.param(None, None, id="none"),
        pytest.param("", "", id="empty_string"),
        pytest.param("string", "string", id="string"),
    ],
)


class BKStrTestBase(FieldTestBase[str]):
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

    @parameterize_bk_strs
    def test__python_ctor(self, value, expected):
        instance = self.ctor(**{self.ATTR_NAME: value})
        assert getattr(instance, self.ATTR_NAME) == expected

    @parameterize_bk_strs
    def test__setter(self, value, expected):
        wait_step = self.ctor()
        setattr(wait_step, self.ATTR_NAME, value)
        assert getattr(wait_step, self.ATTR_NAME) == expected

    @parameterize_bk_strs
    def test__json_load(self, value, expected):
        instance = self.model_load({self.ATTR_NAME: value})
        assert getattr(instance, self.ATTR_NAME) == expected

    # @TODO: Add schema valid/invalid tests
