from shimbboleth.buildkite.pipeline_config import BuildkitePipeline
from shimbboleth.buildkite.pipeline_config.tests.helpers import (
    get_upstream_schema,
    get_generated_schema,
    is_valid_upstream,
)

from pytest import param

from typing import ClassVar, Any


class SchemaTestBase:
    MODEL: ClassVar[type]
    TYPENAME: ClassVar[str]
    VALID_STEPS: ClassVar[list[dict[str, Any]]]
    INVALID_STEPS: ClassVar[list[dict[str, Any]]]

    @classmethod
    def pytest_generate_tests(cls, metafunc):
        if hasattr(SchemaTestBase, metafunc.function.__name__):
            metafunc.parametrize(
                ["step_config", "is_valid"],
                [param(*step_param.values, True, id=step_param.id) for step_param in cls.VALID_STEPS]
                + [param(*step_param.values, False, id=step_param.id) for step_param in cls.INVALID_STEPS],
            )

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
                                "steps": [{cls.TYPENAME: {k: v for k, v in step_config.items() if k != "type"}}]
                            },
                            id="asnesteddict",
                        ),
                    ],
                )

    def test__step_cls__model_load(self, step_config, is_valid: bool):
        try:
            self.MODEL.model_load(step_config)
        except Exception:
            if is_valid:
                raise
        else:
            if not is_valid:
                raise AssertionError("Expected to raise an exception")

    def test__pipeline__model_load(self, step_config, xform, is_valid: bool):
        try:
            BuildkitePipeline.model_load(xform(step_config))
        except Exception:
            if is_valid:
                raise
        else:
            if not is_valid:
                raise AssertionError("Expected to raise an exception")

    def test__pipeline__generated_schema(self, step_config, xform, is_valid: bool):
        errors = list(get_generated_schema().iter_errors(xform(step_config)))
        assert (is_valid and not errors) or (not is_valid and errors)

    def test__pipeline__upstream_schema(self, step_config, xform, is_valid: bool):
        errors = list(get_upstream_schema().iter_errors(xform(step_config)))
        assert (is_valid and not errors) or (not is_valid and errors)

    def test__pipeline__api(self, step_config, xform, is_valid: bool):
        # @TODO: Print a reproducer curl for debugging
        assert is_valid_upstream(xform(step_config)) is is_valid
