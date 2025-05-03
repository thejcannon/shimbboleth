
from shimbboleth.buildkite.pipeline_config.tests.bases.schema import SchemaTestBase
from pytest import param
from typing import ClassVar, Any

class StepNameLabelNameTestBase(SchemaTestBase):
    TYPENAME: ClassVar[str]
    
    VALID_STEPS: ClassVar[list[dict[str, Any]]]
    INVALID_STEPS: ClassVar[list[dict[str, Any]]] = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.VALID_STEPS = [
            param({cls.TYPENAME: cls.TYPENAME, "name": "name"}, id=cls.TYPENAME),
            param({"label": "label", "type": cls.TYPENAME}, id="label"),
            param({"name": "name", "type": cls.TYPENAME}, id="name"),
            param({cls.TYPENAME: cls.TYPENAME, "label": "label"}, id=f"{cls.TYPENAME}-label"),
            param({cls.TYPENAME: cls.TYPENAME, "name": "name"}, id=f"{cls.TYPENAME}-name"),
            param({"label": "label", "name": "name", "type": cls.TYPENAME}, id="label-name"),
            param({cls.TYPENAME: cls.TYPENAME, "label": "label", "name": "name"}, id=f"{cls.TYPENAME}-label-name"),
        ]

    # @TODO: Test precedence

