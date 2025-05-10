from shimbboleth.buildkite.pipeline_config.tests.wait_step.base import TestBase
from shimbboleth.buildkite.pipeline_config.tests.bases.bk_bool import BKBoolTest
from shimbboleth.buildkite.pipeline_config.tests.bases.bk_str_list import (
    BKStrListTest,
    BKStrListDefaultTest,
)
from pytest import param
from shimbboleth.buildkite.pipeline_config.step import Step


class Test_Default(TestBase, BKStrListDefaultTest):
    ATTR_NAME = "depends_on"


class Test_Pipelines(TestBase, BKStrListTest):
    ATTR_NAME = "depends_on"

    PARAMETRIZATIONS = [
        param(None, [], id="none"),
        # Scalars
        param("string", [Step.Dependency(step="string")], id="string"),
        param(1, [Step.Dependency(step="1")], id="int"),
        # Lists
        param(
            ["string1", "string2"],
            [Step.Dependency(step="string1"), Step.Dependency(step="string2")],
            id="list",
        ),
        param([], [], id="empty_list"),
        param(
            [1, 2],
            [Step.Dependency(step="1"), Step.Dependency(step="2")],
            id="int_list",
        ),
        param(
            [1, "2", 3],
            [
                Step.Dependency(step="1"),
                Step.Dependency(step="2"),
                Step.Dependency(step="3"),
            ],
            id="mixed_list",
        ),
        param(
            [{"step": "step"}],
            [Step.Dependency(step="step")],
            id="dict_with_string_step",
        ),
        param([{"step": 1}], [Step.Dependency(step="1")], id="dict_with_int_step"),
        # Allow failure
        *[
            param(
                [{"step": "step", "allow_failure": bool_param.values[0]}],
                [Step.Dependency(step="step", allow_failure=bool_param.values[1])],
                id=f"allow_failure__{bool_param.id}",
            )
            for bool_param in BKBoolTest.PARAMETRIZATIONS
        ],
        # @TODO: test `param([Step.Dependency(...)])`
    ]

    INVALID_STEPS = [
        param({"depends_on": ""}, id="empty_string"),
        param({"depends_on": {}}, id="empty_dict"),
        param({"depends_on": {"step": "step"}}, id="scalar_dict"),
        param({"depends_on": {"allow_failure": True}}, id="missing_step"),
    ]