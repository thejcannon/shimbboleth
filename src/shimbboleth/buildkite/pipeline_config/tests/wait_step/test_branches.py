from shimbboleth.buildkite.pipeline_config.tests.wait_step.base import TestBase
from shimbboleth.buildkite.pipeline_config.tests.bases.bk_str_list import (
    BKStrListTest,
    BKStrListDefaultTest,
)


class Test_Default(TestBase, BKStrListDefaultTest):
    ATTR_NAME = "branches"


class Test_Pipelines(TestBase, BKStrListTest):
    # @TODO: Branches seems special:
    # - It's a str/list[str] but also space-separated?
    ATTR_NAME = "branches"

    # @TODO: All of the invalid pipelines are somehow valid upstream API???
    #   (meaning it accepts any type)
