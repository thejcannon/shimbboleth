from shimbboleth.buildkite.pipeline_config.wait_step import WaitStep
from shimbboleth.buildkite.pipeline_config.tests2.bases.bk_bool import BKBoolTest
import pytest
from pytest import param
from typing import Any
from shimbboleth.buildkite.pipeline_config.tests2.helpers import (
    valid_pipeline_test,
    IsValidPipeline,
)


class Test_Field_ContinueOnFailure(BKBoolTest):
    MODEL = WaitStep
    UPSTREAM_SCHEMA_DEF_NAME = "waitStep"
    DEFAULT = False
    ATTR_NAME = "continue_on_failure"


class Test_Field_Wait:
    """
    Not much to test here, since it really isn't used.

    Just only test cases where it can be noticed.
    """

    @valid_pipeline_test
    @pytest.mark.parametrize(
        "config",
        [
            param({"wait": None}, id="none"),
            param({"wait": ""}, id="empty_string"),
            param({"wait": "a string"}, id="string"),
        ],
    )
    def test__valid_json(
        self, config: dict[str, Any], is_valid_pipeline: IsValidPipeline
    ):
        assert is_valid_pipeline(config)

    @pytest.mark.parametrize(
        "config",
        [
            param({"wait": 1}, id="integer"),
            param({"wait": []}, id="empty_list"),
            param({"wait": {"key": "value"}}, id="dict"),
        ],
    )
    @pytest.mark.xfail(reason="These actually work")
    def test__invalid_json(
        self, config: dict[str, Any], is_valid_pipeline: IsValidPipeline
    ):
        assert not is_valid_pipeline(config)
