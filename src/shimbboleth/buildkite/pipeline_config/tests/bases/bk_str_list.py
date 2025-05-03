from shimbboleth.internal.clay.model import Model
from typing import ClassVar, Any
import pytest
from pytest import param

from shimbboleth.buildkite.pipeline_config.tests.helpers import get_upstream_schema
from shimbboleth.buildkite.pipeline_config.tests.bases.schema import SchemaTestBase

parameterize_bk_str_list = pytest.mark.parametrize(
    "value, expected",
    [
        param("string", ["string"], id="string"),
        param(["string1", "string2"], ["string1", "string2"], id="list"),
        param("", "", id="empty-string"),
        param([], [], id="empty-list"),
        param(None, [], id="none"),
    ],
)

class BKStrListTest(SchemaTestBase):
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

    def __init_subclass__(cls) -> None:
        cls.VALID_STEPS = [
            param({cls.ATTR_NAME:case.values[0], "type": cls.TYPENAME}, id=case.id) for case in parameterize_bk_str_list.args[1]
        ]
        cls.INVALID_STEPS = [
            param({cls.ATTR_NAME: 1, "type": cls.TYPENAME}, id="int"),
            param({cls.ATTR_NAME: [1], "type": cls.TYPENAME}, id="list-int"),
            param({cls.ATTR_NAME: {"key": 1}, "type": cls.TYPENAME}, id="dict"),
        ]

    # ===== TESTS =====

    def test__default(self):
        assert getattr(self.model_load(), self.ATTR_NAME) == []
        assert getattr(self.ctor(), self.ATTR_NAME) == []
        assert (
            self.MODEL.model_json_schema["properties"][self.ATTR_NAME]["default"] == []
        )
    
    def test__default__upstream_schema(self):
        assert (
            get_upstream_schema().schema["definitions"][self.UPSTREAM_SCHEMA_DEF_NAME][
                "properties"
            ][self.ATTR_NAME]["default"] == []
        )

    def test__schema__not_required(self):
        assert self.ATTR_NAME not in self.MODEL.model_json_schema.get("required", [])
        assert self.ATTR_NAME not in get_upstream_schema().schema["definitions"][
            self.UPSTREAM_SCHEMA_DEF_NAME
        ]["properties"].get("required", [])

    def test__model_dump(self):
        assert self.ATTR_NAME not in self.model_load().model_dump()
        assert self.ATTR_NAME not in self.model_load({self.ATTR_NAME: []}).model_dump()
        assert self.ATTR_NAME not in self.model_load({self.ATTR_NAME: None}).model_dump()
        assert (
            self.ATTR_NAME
            in self.model_load({self.ATTR_NAME: ["a"]}).model_dump()
        )

    @parameterize_bk_str_list
    def test__python_ctor(self, value, expected):
        instance = self.ctor(**{self.ATTR_NAME: value})
        assert getattr(instance, self.ATTR_NAME) == expected

    @parameterize_bk_str_list
    def test__setter(self, value, expected):
        instance = self.ctor()
        setattr(instance, self.ATTR_NAME, value)
        assert getattr(instance, self.ATTR_NAME) == expected

    @parameterize_bk_str_list
    def test__json_load(self, value, expected):
        instance = self.model_load({self.ATTR_NAME: value})
        assert getattr(instance, self.ATTR_NAME) == expected

