from shimbboleth.buildkite.pipeline_config import BuildkitePipeline
from shimbboleth.buildkite.pipeline_config.tests.helpers import (
    get_upstream_schema,
    get_generated_schema,
    is_valid_upstream,
)

from pytest import param
import pytest

from typing import ClassVar, Any


class SchemaTestBase:
    MODEL: ClassVar[type]
    TYPENAME: ClassVar[str]
    VALID_STEPS: ClassVar[list[dict[str, Any]]]
    INVALID_STEPS: ClassVar[list[dict[str, Any]]]

    @classmethod
    def pytest_generate_tests(cls, metafunc):
        if hasattr(SchemaTestBase, metafunc.function.__name__):
            steps = (
                cls.INVALID_STEPS
                if "invalid" in metafunc.function.__name__
                else cls.VALID_STEPS
            )
            metafunc.parametrize("step_config", steps)

            if "pipeline" in metafunc.function.__name__:
                metafunc.parametrize(
                    "xform",
                    [
                        param(lambda step_config: [step_config], id="aslist"),
                        param(
                            lambda step_config: {"steps": [step_config]}, id="asdict"
                        ),
                        param(
                            lambda step_config: {
                                # NB: `type: ` isn't valid on nested steps (since the nesting already disambiguates)
                                "steps": [
                                    {
                                        cls.TYPENAME: {
                                            k: v
                                            for k, v in step_config.items()
                                            if k != "type"
                                        }
                                    }
                                ]
                            },
                            id="asnesteddict",
                        ),
                    ],
                )

    def test__valid__step_cls__model_load(self, step_config):
        self.MODEL.model_load(step_config)

    def test__invalid__step_cls__model_load(self, step_config):
        with pytest.raises(Exception):
            self.MODEL.model_load(step_config)

    def test__valid__pipeline__model_load(self, step_config, xform):
        BuildkitePipeline.model_load(xform(step_config))

    def test__invalid__pipeline__model_load(self, step_config, xform):
        with pytest.raises(Exception):
            BuildkitePipeline.model_load(xform(step_config))

    def test__valid__pipeline__generated_schema(self, step_config, xform):
        assert not list(get_generated_schema().iter_errors(xform(step_config)))

    def test__invalid__pipeline__generated_schema(self, step_config, xform):
        assert list(get_generated_schema().iter_errors(xform(step_config)))

    def test__valid__pipeline__upstream_schema(self, step_config, xform):
        assert not list(get_upstream_schema().iter_errors(xform(step_config)))

    def test__invalid__pipeline__upstream_schema(self, step_config, xform):
        assert list(get_upstream_schema().iter_errors(xform(step_config)))

    def test__valid__pipeline__api(self, step_config, xform):
        # @TODO: Print a reproducer curl for debugging
        assert is_valid_upstream(xform(step_config))

    def test__invalid__pipeline__api(self, step_config, xform):
        # @TODO: Print a reproducer curl for debugging
        assert not is_valid_upstream(xform(step_config))
