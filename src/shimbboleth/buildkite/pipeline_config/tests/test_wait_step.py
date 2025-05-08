from shimbboleth.buildkite.pipeline_config.tests.bases.bk_str import BKStrTestBase
from shimbboleth.buildkite.pipeline_config.wait_step import WaitStep
from shimbboleth.buildkite.pipeline_config.tests.bases.bk_bool import BKBoolTest
from shimbboleth.buildkite.pipeline_config.tests.bases.bk_str_list import (
    BKStrListTestBase,
)
from pytest import param
from shimbboleth.buildkite.pipeline_config.tests.bases.schema import SchemaTestBase
from shimbboleth.buildkite.pipeline_config.tests.bases.stepname_label_name import (
    StepNameLabelNameTestBase,
)
from shimbboleth.buildkite.pipeline_config.step import Step


class WaitStepTestBase:
    MODEL = WaitStep
    UPSTREAM_SCHEMA_DEF_NAME = "waitStep"
    TYPENAME = "wait"


class Test_Field__Key(WaitStepTestBase, BKStrTestBase):
    ATTR_NAME = "key"
    DEFAULT = None

    # @TODO: "Step keys may only contain alphanumeric characters, underscores, dashes and colons"

    VALID_STEPS = [
        param(
            {"key": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", "type": "wait"},
            id="uuid_format_with_x",
        ),
        param(
            {"key": "12345678-1234-1234-1234-1234567890123456", "type": "wait"},
            id="uuid_too_long",
        ),
        param(
            {"key": "12345678-1234-1234-1234-123", "type": "wait"}, id="uuid_too_short"
        ),
        param(
            {"key": "test-12345678-1234-1234-1234-123456789012", "type": "wait"},
            id="uuid_with_prefix",
        ),
    ]

    INVALID_STEPS = [
        param(
            {"key": "550e8400-e29b-41d4-a716-446655440000", "type": "wait"},
            id="uuid_v4",
        ),
        param(
            {"key": "6ba7b810-9dad-11d1-80b4-00c04fd430c8", "type": "wait"},
            id="uuid_v1",
        ),
        param(
            {"key": "6ba7b810-9dad-11d1-80b4-00c04fd430c8", "type": "wait"},
            id="uuid_v3",
        ),
        param(
            {"key": "6ba7b814-9dad-11d1-80b4-00c04fd430c8", "type": "wait"},
            id="uuid_v5",
        ),
        param(
            {"key": "123e4567-e89b-12d3-a456-426614174000", "type": "wait"},
            id="another_uuid",
        ),
    ]


class Test_Field__AllowDependencyFailure(WaitStepTestBase, BKBoolTest):
    DEFAULT = False
    ATTR_NAME = "allow_dependency_failure"


class Test_Field__DependsOn(WaitStepTestBase, BKStrListTestBase):
    DEFAULT = []
    ATTR_NAME = "depends_on"

    PARAMETERIZATIONS = [
        param(None, [], id="none"),
        # Scalars
        param("string", [Step.Dependency(step="string")], id="string"),
        param(1, [Step.Dependency(step="1")], id="int"),
        # Lists
        param(["string1", "string2"], [Step.Dependency(step="string1"), Step.Dependency(step="string2")], id="list"),
        param([], [], id="empty_list"),
        param([1, 2], [Step.Dependency(step="1"), Step.Dependency(step="2")], id="int_list"),
        param([1, "2", 3], [Step.Dependency(step="1"), Step.Dependency(step="2"), Step.Dependency(step="3")], id="mixed_list"),
        param([{"step": "step"}], [Step.Dependency(step="step")], id="dict_with_string_step"),
        param([{"step": 1}], [Step.Dependency(step="1")], id="dict_with_int_step"),


        # @TODO: allow_failure inside `depends_on`
    ]

    INVALID_STEPS = [
        param({"depends_on": ""}, id="empty_string"),
        param({"step": "step"}, id="scalar_dict"),
    ]


class Test_Field__Branches(WaitStepTestBase, BKStrListTestBase):
    # @TODO: Branches seems special:
    # - It's a str/list[str] but also space-separated?
    DEFAULT = []
    ATTR_NAME = "branches"

    # @TODO: All of the invalid pipelines are somehow valid upstream API???
    #   (meaning it accepts any type)


class Test_Field__ContinueOnFailure(WaitStepTestBase, BKBoolTest):
    DEFAULT = False
    ATTR_NAME = "continue_on_failure"


class Test_Field__Wait(WaitStepTestBase, SchemaTestBase):
    VALID_STEPS = [
        param({"wait": None}, id="none"),
        param({"wait": ""}, id="empty_string"),
        param({"wait": "a string"}, id="string"),
        param({"wait": 1}, id="int"),
        param({"wait": []}, id="empty_list"),
        # param({"wait": {"key": "value"}}, id="dict"),
    ]

    INVALID_STEPS = []


# @TODO: Move this to some other file?
class Test_Field__Type(WaitStepTestBase, SchemaTestBase):
    VALID_STEPS = [
        param({"type": "wait"}, id="wait"),
        param({"type": "waiter"}, id="waiter"),
    ]

    INVALID_STEPS = [
        # param({"wait": None, "type": 1}, id="integer"),
        # param({"wait": None, "type": []}, id="empty_list"),
        # param({"wait": None, "type": {"key": "value"}}, id="dict"),
    ]


class Test_Field__WaitLabelName(WaitStepTestBase, StepNameLabelNameTestBase):
    pass
