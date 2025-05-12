from shimbboleth.buildkite.pipeline_config.tests.wait_step.base import TestBase
from pytest import param
from shimbboleth.buildkite.pipeline_config.tests.bases.schema import SchemaTest


class Test_Wait(TestBase, SchemaTest):
    VALID_STEPS = [
        param({"wait": None}, id="none"),
        param({"wait": ""}, id="empty_string"),
        param({"wait": "a string"}, id="string"),
        param({"wait": 1}, id="int"),
        param({"wait": []}, id="empty_list"),
        # param({"wait": {"key": "value"}}, id="dict"),
    ]

    INVALID_STEPS = []
