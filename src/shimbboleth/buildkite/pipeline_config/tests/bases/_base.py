from typing import ClassVar, Any
from shimbboleth.internal.clay.model import Model
from shimbboleth.buildkite.pipeline_config.tests.helpers import get_upstream_schema


class FieldTestBase:
    MODEL: ClassVar[type[Model]]
    UPSTREAM_SCHEMA_DEF_NAME: ClassVar[str]
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


class DefaultTestBase(FieldTestBase):
    """
    A base class for testing fields with a default value.

    This class is used to test the default value of a field in a model.
    It is not intended to be used directly, but rather as a base class for
    other test classes.
    """

    DEFAULT: ClassVar

    def test_value(self):
        assert getattr(self.model_load(), self.ATTR_NAME) == self.DEFAULT
        assert getattr(self.ctor(), self.ATTR_NAME) == self.DEFAULT
        assert (
            self.MODEL.model_json_schema["properties"][self.ATTR_NAME]["default"]
            == self.DEFAULT
        )

    def test_upstream_schema(self):
        assert (
            get_upstream_schema().schema["definitions"][self.UPSTREAM_SCHEMA_DEF_NAME][
                "properties"
            ][self.ATTR_NAME]["default"]
            == self.DEFAULT
        )

    def test_schema_not_required(self):
        assert self.ATTR_NAME not in self.MODEL.model_json_schema.get("required", [])
        assert self.ATTR_NAME not in get_upstream_schema().schema["definitions"][
            self.UPSTREAM_SCHEMA_DEF_NAME
        ]["properties"].get("required", [])
