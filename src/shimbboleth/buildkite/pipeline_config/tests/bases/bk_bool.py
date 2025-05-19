from pytest import param

from shimbboleth.buildkite.pipeline_config.tests.bases._base import DefaultTestBase
from shimbboleth.buildkite.pipeline_config.tests.bases.field import FieldTest


class BKBoolTest(FieldTest):
    PARAMETRIZATIONS = [
        param(True, True, id="True"),
        param("true", True, id="true"),
        param(False, False, id="False"),
        param("false", False, id="false"),
        # @TODO: Should `None` instead be the default? Or the default?
        param(None, False, id="None"),
    ]

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls.INVALID_STEPS += [
            # @TODO: Add cases (but also BK seems to just be OK with any value???)
        ]


class BKBoolDefaultTest(DefaultTestBase):
    def test__model_dump(self):
        assert self.FIELD_NAME not in self.model_load().model_dump()
        assert (
            self.FIELD_NAME
            not in self.model_load({self.FIELD_NAME: self.DEFAULT}).model_dump()
        )
        opposite = not self.DEFAULT
        assert (
            self.model_load({self.FIELD_NAME: opposite}).model_dump()[self.FIELD_NAME]
            is opposite
        )
