from shimbboleth.internal.clay.model import Model
from typing import ClassVar, Any
import pytest

from shimbboleth.buildkite.pipeline_config.tests.helpers import get_upstream_schema

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


class BKBoolTest:
    MODEL: ClassVar[type[Model]]
    UPSTREAM_SCHEMA_DEF_NAME: ClassVar[str]
    DEFAULT: ClassVar[bool]
    ATTR_NAME: ClassVar[str]

    @classmethod
    def ctor(cls, **kwargs) -> Model:
        """
        Construct a new instance of the model.

        Subclasses can override.
        """
        return cls.MODEL(**kwargs)

    @classmethod
    def model_load(cls, data: dict[str, Any] = {}) -> Model:
        """
        Load a new instance of the model from a JSON object.

        Subclasses can override.
        """
        return cls.MODEL.model_load(data)

    # ===== TESTS =====

    def test__default(self):
        assert getattr(self.model_load(), self.ATTR_NAME) is self.DEFAULT
        assert getattr(self.ctor(), self.ATTR_NAME) is self.DEFAULT
        assert (
            self.MODEL.model_json_schema["properties"][self.ATTR_NAME]["default"]
            is self.DEFAULT
        )
        assert (
            get_upstream_schema().schema["definitions"][self.UPSTREAM_SCHEMA_DEF_NAME][
                "properties"
            ][self.ATTR_NAME]["default"]
            is self.DEFAULT
        )

    def test__schema__not_required(self):
        assert self.ATTR_NAME not in self.MODEL.model_json_schema.get("required", [])
        assert self.ATTR_NAME not in get_upstream_schema().schema["definitions"][
            self.UPSTREAM_SCHEMA_DEF_NAME
        ]["properties"].get("required", [])

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
