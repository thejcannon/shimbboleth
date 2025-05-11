from shimbboleth.buildkite.pipeline_config.tests.wait_step.base import TestBase
from shimbboleth.buildkite.pipeline_config.tests.bases.bk_bool import (
    BKBoolDefaultTest,
    BKBoolTest,
)


class Test_Default(TestBase, BKBoolDefaultTest):
    ATTR_NAME = "continue_on_failure"
    DEFAULT = False


class Test_Pipelines(TestBase, BKBoolTest):
    ATTR_NAME = "continue_on_failure"
