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


class WaitStepTestBase:
    MODEL = WaitStep
    UPSTREAM_SCHEMA_DEF_NAME = "waitStep"
    TYPENAME = "wait"


class Test_Field__Key(WaitStepTestBase, BKStrTestBase):
    ATTR_NAME = "key"
    DEFAULT = None



    # @TODO: UUID stuff (SCHEMA_VALID and SCHEMA_INVALID)


class Test_Field__Branches(WaitStepTestBase, BKStrListTestBase):
    # @TODO: Branches seems special:
    # - It's a str/list[str] but also space-separated?
    ATTR_NAME = "branches"
    DEFAULT = []

    # @TODO: All of the invalid pipelines are somehow valid upstream API???

class Test_Field__ContinueOnFailure(WaitStepTestBase, BKBoolTest):
    DEFAULT = False
    ATTR_NAME = "continue_on_failure"


class Test_Field__Wait(WaitStepTestBase, SchemaTestBase):
    VALID_STEPS = [
        param({"wait": None}, id="none"),
        param({"wait": ""}, id="empty_string"),
        param({"wait": "a string"}, id="string"),
        param({"wait": 1}, id="integer"),
        param({"wait": []}, id="empty_list"),
        param({"wait": {"key": "value"}}, id="dict"),
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
