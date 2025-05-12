from shimbboleth.buildkite.pipeline_config.tests.wait_step.base import TestBase
from pytest import param
from shimbboleth.buildkite.pipeline_config.tests.bases.schema import SchemaTest


# @TODO: Move this to some other file?
class Test_Type(TestBase, SchemaTest):
    VALID_STEPS = [
        param({"type": "wait"}, id="wait"),
        param({"type": "waiter"}, id="waiter"),
    ]

    INVALID_STEPS = [
        # param({"wait": None, "type": 1}, id="integer"),
        # param({"wait": None, "type": []}, id="empty_list"),
        # param({"wait": None, "type": {"key": "value"}}, id="dict"),
    ]
