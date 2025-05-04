from typing import ClassVar, Any, Generic, TypeVar
from shimbboleth.internal.clay.model import Model
from shimbboleth.buildkite.pipeline_config.tests.helpers import get_upstream_schema

T = TypeVar("T")


class FieldTestBase(Generic[T]):
    MODEL: ClassVar[type[Model]]
    UPSTREAM_SCHEMA_DEF_NAME: ClassVar[str]
    DEFAULT: ClassVar[T | None]
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

    def test__default(self):
        assert getattr(self.model_load(), self.ATTR_NAME) == self.DEFAULT
        assert getattr(self.ctor(), self.ATTR_NAME) == self.DEFAULT
        assert (
            self.MODEL.model_json_schema["properties"][self.ATTR_NAME]["default"]
            == self.DEFAULT
        )

    def test__default__upstream_schema(self):
        assert (
            get_upstream_schema().schema["definitions"][self.UPSTREAM_SCHEMA_DEF_NAME][
                "properties"
            ][self.ATTR_NAME]["default"]
            == self.DEFAULT
        )

    def test__schema__not_required(self):
        assert self.ATTR_NAME not in self.MODEL.model_json_schema.get("required", [])
        assert self.ATTR_NAME not in get_upstream_schema().schema["definitions"][
            self.UPSTREAM_SCHEMA_DEF_NAME
        ]["properties"].get("required", [])
