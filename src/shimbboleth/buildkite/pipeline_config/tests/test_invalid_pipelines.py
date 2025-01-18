"""
@TODO: ...

"""

from shimbboleth.buildkite.pipeline_config import (
    BuildkitePipeline,
    get_schema,
)
from shimbboleth.buildkite.pipeline_config.tests.conftest import (
    STEP_TYPE_PARAMS,
    ALL_STEP_TYPE_PARAMS,
)

import pytest
import jsonschema
import jsonschema.exceptions
from pytest import param

# @TODO: Tests for extra keys!


class PipelineTestBase:
    def test_fails_to_load(self, config, *, error, path):
        # @TODO: ValidationError
        with pytest.raises(Exception) as e:
            print(BuildkitePipeline.model_load(config))
        assert error in str(e.value)
        assert f"Path: {path}\n" in str(e.value) + "\n"

    def test_pipeline_invalid(self, config, *, error, path):
        with pytest.raises(jsonschema.exceptions.ValidationError):
            jsonschema.validate(config, get_schema())


class StepTestBase(PipelineTestBase):
    def get_step(self, step, steptype_param):
        return {**step, "type": steptype_param.stepname}

    def test_fails_to_load(self, step, steptype_param, *, error, path):  # type: ignore
        step = self.get_step(step, steptype_param)
        super().test_fails_to_load(
            {"steps": [step]}, error=error, path=f".steps[0]{path}"
        )

    @pytest.mark.skip()
    def test_pipeline_invalid(self, step, steptype_param, *, error, path):  # type: ignore
        step = self.get_step(step, steptype_param)
        super().test_pipeline_invalid({"steps": [step]}, error=error, path=path)


@pytest.mark.parametrize(
    ["config", "error", "path"],
    [
        param(
            ["unknown"], "Unrecognizable step: `'unknown'`", "[0]", id="unknown_step"
        ),
        param([None], "Unrecognizable step: `None`", "[0]", id="null_step"),
        param(
            [{"type": "unknown"}],
            "Unrecognizable step: `{'type': 'unknown'}`",
            "[0]",
            id="unknown_type",
        ),
        param(
            {"steps": [], "env": ["key"]},
            "Expected `dict`, got `['key']` of type `list`",
            ".env",
            id="env_list",
        ),
        param(
            {"steps": [], "notify": ["unknown"]},
            "Unrecognizable notification: `unknown`",
            ".notify[0]",
            id="notify_unknown",
        ),
        param(
            {"steps": [], "notify": [{"unknown": ""}]},
            "Unrecognizable notification: `unknown`",
            ".notify[0]",
            id="notify_unknown_dict",
        ),
        param(
            {"steps": [], "notify": [{"slack": {"channels": []}}]},
            "Expected `[]` to be non-empty",
            ".notify[0].slack.channels",
            id="notify_slack_empty_channels",
        ),
    ],
)
class Test_InvalidPipeline(PipelineTestBase):
    pass


@pytest.mark.parametrize("steptype_param", ALL_STEP_TYPE_PARAMS)
@pytest.mark.parametrize(
    ["step", "error", "path"],
    [
        param(
            {"key": "2cb75f85-79ab-43a0-b666-91dbcb64321a"},
            "Expected `'2cb75f85-79ab-43a0-b666-91dbcb64321a'` to not be a valid UUID",
            ".key",
            id="key_uuid",
        ),
        param(
            {"depends_on": [{}]},
            "`Dependency` missing 1 required fields: `step`",
            ".depends_on[0]",
            id="depends_on_missing_step",
        ),
    ],
)
class Test_AnyStepType(StepTestBase):
    def get_step(self, step, steptype_param):
        return {**step, **steptype_param.dumped_default}


@pytest.mark.parametrize(
    "steptype_param", [STEP_TYPE_PARAMS["block"], STEP_TYPE_PARAMS["input"]]
)
@pytest.mark.parametrize(
    "step,error,path",
    [
        param(
            {"fields": [{}]},
            "Input fields must contain `text`` or `select`",
            ".fields[0]",
            id="missing_field_type",
        ),
    ],
)
class Test_ManualStep(StepTestBase):
    def get_step(self, step, steptype_param):
        return {
            "type": steptype_param.stepname,
            **step,
        }


@pytest.mark.parametrize(
    "steptype_param", [STEP_TYPE_PARAMS["block"], STEP_TYPE_PARAMS["input"]]
)
@pytest.mark.parametrize(
    "step,error,path",
    [
        param(
            {"text": "text"},
            "`TextInput` missing 1 required fields: `key`",
            ".fields[0]",
            id="missing_text_key",
        ),
        param(
            {"text": "text", "key": "has:a:colon"},
            "Expected `'has:a:colon'` to match regex `^[a-zA-Z0-9-_]+$`",
            ".fields[0].key",
            id="bad_key_colon",
        ),
        param(
            {"text": "text", "key": "has a space"},
            "Expected `'has a space'` to match regex `^[a-zA-Z0-9-_]+$`",
            ".fields[0].key",
            id="bad_key_space",
        ),
        param(
            {"text": "text", "key": "key", "format": "'[a-zA-Z++++'"},
            "Expected a valid regex pattern, got `\"'[a-zA-Z++++'\"",
            ".fields[0].format",
            id="invalid_regex",
        ),
    ],
)
class Test_ManualStep__InvalidTextField(StepTestBase):
    def get_step(self, step, steptype_param):
        return {"type": steptype_param.stepname, "fields": [step]}


@pytest.mark.parametrize(
    "steptype_param", [STEP_TYPE_PARAMS["block"], STEP_TYPE_PARAMS["input"]]
)
@pytest.mark.parametrize(
    "step,error,path",
    [
        param(
            {
                "select": "select",
                "key": "has:a:colon",
                "options": [{"label": "label", "value": "value"}],
            },
            "Expected `'has:a:colon'` to match regex `^[a-zA-Z0-9-_]+$`",
            ".fields[0].key",
            id="bad_key_colon",
        ),
        param(
            {
                "select": "select",
                "key": "has a space",
                "options": [{"label": "label", "value": "value"}],
            },
            "Expected `'has a space'` to match regex `^[a-zA-Z0-9-_]+$`",
            ".fields[0].key",
            id="bad_key_space",
        ),
        param(
            {
                "select": "select",
                "key": "key",
                "options": [{"label": "label", "value": "value"}],
                "multiple": False,
                "default": ["value"],
            },
            "`default` cannot be a list when `multiple` is `False`",
            ".fields[0]",
            id="single_select_list_default",
        ),
        param(
            {"select": "select", "options": [{"label": "label", "value": "value"}]},
            "`SelectInput` missing 1 required fields: `key`",
            ".fields[0]",
            id="missing_select_key",
        ),
        param(
            {"select": "select", "key": "key"},
            "`SelectInput` missing 1 required fields: `options`",
            ".fields[0]",
            id="missing_options",
        ),
        param(
            {"select": "select", "key": "key", "options": []},
            "Expected `[]` to be non-empty",
            ".fields[0].options",
            id="empty_options",
        ),
    ],
)
class Test_ManualStep__InvalidSelectField(StepTestBase):
    def get_step(self, step, steptype_param):
        return {"type": steptype_param.stepname, "fields": [step]}


@pytest.mark.parametrize("steptype_param", [STEP_TYPE_PARAMS["command"]])
@pytest.mark.parametrize(
    "step,error,path",
    [
        param(
            {"plugins": [{"key1": {}, "key2": {}}]},
            "...",
            ".plugins[0]",
            id="plugins_multiple_props",
            marks=pytest.mark.xfail(reason="not implemented yet"),
        ),
        param(
            {"cache": {}},
            "`CommandCache` missing 1 required fields: `paths`",
            ".cache",
            id="cache_missing_paths",
        ),
        param(
            {"cache": {"paths": [], "size": "1"}},
            "Expected `'1'` to match regex `^\\d+g$`",
            ".cache.size",
            id="cache_bad_size",
        ),
        param(
            {"retry": {"automatic": [{"limit": 11}]}},
            "Expected `11` to be <= 10",
            ".retry.automatic[0].limit",
            id="retry_big_limit",
        ),
    ],
)
class Test_CommandStep(StepTestBase):
    pass


@pytest.mark.parametrize("steptype_param", [STEP_TYPE_PARAMS["command"]])
@pytest.mark.parametrize(
    "step,error,path",
    [
        param(
            ["unknown"],
            "Unrecognizable notification: `unknown`",
            ".notify[0]",
            id="notify_unknown",
        ),
        param(
            [{"email": "hello@example.com"}],
            "`email` is not a valid step notification",
            ".notify[0]",
            id="notify_email",
        ),
        param(
            [{"webhook": "https://example.com"}],
            "`webhook` is not a valid step notification",
            ".notify[0]",
            id="notify_webhook",
        ),
        param(
            [{"pagerduty_change_event": "pagerduty_change_event"}],
            "`pagerduty_change_event` is not a valid step notification",
            ".notify[0]",
            id="notify_pagerduty",
        ),
        param(
            [{"slack": {"channels": []}}],
            "Expected `[]` to be non-empty",
            ".notify[0].slack.channels",
            id="notify_slack_empty",
        ),
    ],
)
class Test_CommandStep__Notify(StepTestBase):
    def get_step(self, step, steptype_param):
        return {"type": "command", "notify": step}


@pytest.mark.parametrize("steptype_param", [STEP_TYPE_PARAMS["command"]])
@pytest.mark.parametrize(
    "step,error,path",
    [
        param(
            {"setup": []},
            "Expected `[]` to be non-empty",
            ".matrix.setup",
            id="matrix_empty_setup",
        ),
        param(
            {"setup": [""], "adjustments": [{"with": {"": ""}}]},
            "Expected `str`, got `{'': ''}` of type `dict`",
            ".matrix.adjustments[0].with_value",
            id="matrix_single_mismatched_adj",
        ),
        param(
            {"setup": {"": []}, "adjustments": [{"with": []}]},
            "Expected `dict`, got `[]` of type `list`",
            ".matrix.adjustments[0].with_value",
            id="matrix_multi_mismatched_adj",
        ),
        param(
            {"setup": {}},
            "Expected `{}` to be non-empty",
            ".matrix.setup",
            id="matrix_empty_setup_dict",
        ),
        param(
            {"setup": [""], "adjustments": [{}]},
            "`ScalarAdjustment` missing 1 required fields: `with_value`",
            ".matrix.adjustments[0]",
            id="matrix_single_empty_adj",
        ),
        param(
            {"setup": {"a": ["b"]}, "adjustments": [{}]},
            "`MultiDimensionMatrixAdjustment` missing 1 required fields: `with_value`",
            ".matrix.adjustments[0]",
            id="matrix_multi_empty_adj",
        ),
        param(
            {"setup": {"": []}},
            "Expected `''` to match regex `^[a-zA-Z0-9_]+$",
            ".matrix.setup (key '')",
            id="matrix_bad_key",
        ),
    ],
)
class Test_CommandStep__Matrix(StepTestBase):
    def get_step(self, step, steptype_param):
        return {"type": "command", "matrix": step}


@pytest.mark.parametrize("steptype_param", [STEP_TYPE_PARAMS["trigger"]])
@pytest.mark.parametrize(
    "step,error,path",
    [
        param(
            {},
            "`TriggerStep` missing 1 required fields: `trigger`",
            "",
            id="missing_trigger",
        ),
    ],
)
class Test_TriggerStep(StepTestBase):
    pass


@pytest.mark.parametrize("steptype_param", [STEP_TYPE_PARAMS["group"]])
@pytest.mark.parametrize(
    "step,error,path",
    [
        param(
            {}, "`GroupStep` missing 1 required fields: `steps`", "", id="missing_steps"
        ),
        param(
            {"steps": []}, "Expected `[]` to be non-empty", ".steps", id="empty_steps"
        ),
    ],
)
class Test_GroupStep(StepTestBase):
    def get_step(self, step, steptype_param):
        return {**step, "group": "group"}


@pytest.mark.parametrize("steptype_param", [STEP_TYPE_PARAMS["group"]])
@pytest.mark.parametrize(
    "step,error,path",
    [
        param(
            ["unknown"],
            "Unrecognizable notification: `unknown`",
            ".notify[0]",
            id="notify_unknown",
        ),
        param(
            [{"email": "hello@example.com"}],
            "`email` is not a valid step notification",
            ".notify[0]",
            id="notify_email",
        ),
        param(
            [{"webhook": "https://example.com"}],
            "`webhook` is not a valid step notification",
            ".notify[0]",
            id="notify_webhook",
        ),
        param(
            [{"pagerduty_change_event": "pagerduty_change_event"}],
            "`pagerduty_change_event` is not a valid step notification",
            ".notify[0]",
            id="notify_pagerduty",
        ),
        param(
            [{"slack": {"channels": []}}],
            "Expected `[]` to be non-empty",
            ".notify[0].slack.channels",
            id="notify_slack_empty",
        ),
    ],
)
class Test_GroupStep__Notify(StepTestBase):
    def get_step(self, step, steptype_param):
        return {"group": "group", "steps": ["wait"], "notify": step}


@pytest.mark.parametrize("steptype_param", [STEP_TYPE_PARAMS["block"]])
@pytest.mark.parametrize("step,error,path", [])
class Test_BlockStep(StepTestBase):
    pass


@pytest.mark.parametrize("steptype_param", [STEP_TYPE_PARAMS["input"]])
@pytest.mark.parametrize("step,error,path", [])
class Test_InputStep(StepTestBase):
    pass


@pytest.mark.parametrize("steptype_param", [STEP_TYPE_PARAMS["wait"]])
@pytest.mark.parametrize("step,error,path", [])
class Test_WaitStep(StepTestBase):
    pass
