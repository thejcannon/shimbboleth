from shimbboleth.buildkite.pipeline_config.tests.bases.bk_str import BKStrDefaultTest, BKStrTest
from shimbboleth.buildkite.pipeline_config.tests.wait_step.base import TestBase
from shimbboleth.buildkite.pipeline_config.tests.bases.schema import SchemaTest
from shimbboleth.buildkite.pipeline_config.tests.bases._base import (
    DefaultTestBase,
    FieldTestBase,
)
from pytest import param, Metafunc


class Test_Default(TestBase, BKStrDefaultTest):
    DEFAULT = None
    ATTR_NAME = "if_condition"
    FIELD_NAME = "if"


class Test_Pipelines(TestBase, BKStrTest):
    ATTR_NAME = "if_condition"
    FIELD_NAME = "if"

    PARAMETRIZATIONS = [
        param(None, None, id="none"),
        param("", "", id="empty_string"),
        # NB: Have to use a valid conditional string
        param("true", "true", id="string"),
        param({}, None, id="empty_dict"),
        param([], None, id="empty_list"),
    ]

    # Even though `if` is a string, it doesn't allow ints,
    # like other string fields do
    INVALID_STEPS = [
        param({"if": 1, "type": "wait"}, id="int"),
    ]
