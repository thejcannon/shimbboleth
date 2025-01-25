"""
Tests using invalid pipelines (according to the schema).

Most of this module is best described by reading `test_schema_valid_pipelines.py`'s docstring
and flipping "valid" for "invalid". However there are some additions to this one:
    - We test the error's given message
    - We test the error's given "Path: "

NOTE: (Same NOTE as in `test_schema_valid_pipelines.py`)
"""

from shimbboleth.buildkite.pipeline_config import (
    BuildkitePipeline,
)
from shimbboleth.buildkite.pipeline_config.tests.conftest import (
    STEP_TYPE_PARAMS,
    ALL_STEP_TYPE_PARAMS,
)
from shimbboleth.internal.clay.validation import ValidationError

import pytest
import yaml
import jsonschema
import jsonschema.exceptions
from pytest import param

# @TODO: Tests for extra keys!

UPSTREAM_SCHEMA_INVALID = pytest.mark.meta(upstream_schema_valid=False)
UPSTREAM_API_500 = pytest.mark.meta(upstream_api_500=True)
UPSTREAM_API_OK = pytest.mark.meta(upstream_api_200=True)


class PipelineTestBase:
    def test_model_load(self, config, *, error, path):
        with pytest.raises(ValidationError) as e:
            print(BuildkitePipeline.model_load(config))
        assert error in str(e.value)
        assert f"Path: {path}\n" in str(e.value) + "\n"

    def test_generated_json_schema(self, config, generated_schema, *, error, path):
        with pytest.raises(jsonschema.exceptions.ValidationError):
            generated_schema.validate(config)

    def test_upstream_json_schema(
        self, config, upstream_schema, request, *, error, path
    ):
        # @TODO: This is duplicated with the valid test
        meta = request.node.get_closest_marker("meta")
        if meta and not meta.kwargs.get("upstream_schema_valid", True):
            pytest.xfail("Upstream schema bug")

        with pytest.raises(jsonschema.exceptions.ValidationError):
            upstream_schema.validate(config)

    @pytest.mark.integration
    def test_upstream_API(self, config, cached_bk_api, *, error, path, request):
        meta = request.node.get_closest_marker("meta")
        if meta and meta.kwargs.get("upstream_api_500", False):
            pytest.skip("Broken in the upstream API - Returns 500")
        if meta and meta.kwargs.get("upstream_api_200", False):
            pytest.xfail("Upstream API returns 200")

        response = cached_bk_api.patch(
            "/organizations/thejcannon/pipelines/step-blaster",
            json={"configuration": yaml.dump(config, default_flow_style=False)},
        )
        print(response.json())
        assert response.status_code == 422


class StepTestBase(PipelineTestBase):
    def get_step(self, step, steptype_param):
        return {**step, "type": steptype_param.stepname}

    def test_model_load(self, step, steptype_param, *, error, path):  # type: ignore
        step = self.get_step(step, steptype_param)
        super().test_model_load({"steps": [step]}, error=error, path=f".steps[0]{path}")

    def test_generated_json_schema(  # type: ignore
        self, step, steptype_param, generated_schema, *, error, path
    ):
        step = self.get_step(step, steptype_param)
        super().test_generated_json_schema(
            {"steps": [step]}, generated_schema=generated_schema, error=error, path=path
        )

    def test_upstream_json_schema(  # type: ignore
        self, step, steptype_param, upstream_schema, request, *, error, path
    ):
        step = self.get_step(step, steptype_param)
        super().test_upstream_json_schema(
            {"steps": [step]},
            upstream_schema=upstream_schema,
            request=request,
            error=error,
            path=path,
        )

    @pytest.mark.integration
    def test_upstream_API(
        self, step, steptype_param, cached_bk_api, request, *, error, path
    ):  # type: ignore
        step = self.get_step(step, steptype_param)
        super().test_upstream_API(
            {"steps": [step]},
            cached_bk_api=cached_bk_api,
            request=request,
            error=error,
            path=path,
        )


@pytest.mark.parametrize(
    ["config", "error", "path"],
    [
        param(
            ["unknown"],
            "Expected `'unknown'` to be a valid Buildkite pipeline step",
            "[0]",
            id="unknown_step",
        ),
        param(
            [None],
            "Expected `None` to be a valid Buildkite pipeline step",
            "[0]",
            id="null_step",
        ),
        param(
            [{"type": "unknown"}],
            "Expected `{'type': 'unknown'}` to be a valid Buildkite pipeline step",
            "[0]",
            id="unknown_type",
        ),
        param(
            {"steps": [], "env": ["key"]},
            "Expected `['key']` to be of type `dict`",
            ".env",
            id="env_list",
            marks=UPSTREAM_API_500,
        ),
        param(
            {"steps": [], "notify": ["unknown"]},
            "Expected `'unknown'` to be a valid notification type",
            ".notify[0]",
            id="notify_unknown",
        ),
        param(
            {"steps": [], "notify": [{"unknown": ""}]},
            "Expected `{'unknown': ''}` to be a valid notification type",
            ".notify[0]",
            id="notify_unknown_dict",
        ),
        param(
            {"steps": [], "notify": [{"slack": {"channels": []}}]},
            "Expected `[]` to be non-empty",
            ".notify[0].slack.channels",
            id="notify_slack_empty_channels",
            marks=UPSTREAM_SCHEMA_INVALID,
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
            "Expected required fields `'step'` to be provided for model `Step.Dependency`",
            ".depends_on[0]",
            id="depends_on_missing_step",
            marks=UPSTREAM_SCHEMA_INVALID,
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
            "Expected `{}` to contain `text` or `select`",
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
            "Expected required fields `'key'` to be provided for model `TextInput`",
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
            "Expected `\"'[a-zA-Z++++'\"` to be a valid regex pattern",
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
            "Expected `['value']` to be a list when `multiple` is `False`",
            ".fields[0]",
            id="single_select_list_default",
            marks=UPSTREAM_SCHEMA_INVALID,
        ),
        param(
            {"select": "select", "options": [{"label": "label", "value": "value"}]},
            "Expected required fields `'key'` to be provided for model `SelectInput`",
            ".fields[0]",
            id="missing_select_key",
        ),
        param(
            {"select": "select", "key": "key"},
            "Expected required fields `'options'` to be provided for model `SelectInput`",
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
            "Expected `{'key1': {}, 'key2': {}}` to have only one key",
            ".plugins[0]",
            id="plugins_multiple_props",
            marks=UPSTREAM_API_OK,
        ),
        param(
            {"cache": {}},
            "Expected required fields `'paths'` to be provided for model `CommandStep.Cache`",
            ".cache",
            id="cache_missing_paths",
            marks=UPSTREAM_API_OK,
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
            "Expected `'unknown'` to be a valid notification type",
            ".notify[0]",
            id="notify_unknown",
        ),
        param(
            [{"email": "hello@example.com"}],
            "Expected `'email'` to be a valid step notification",
            ".notify[0]",
            id="notify_email",
        ),
        param(
            [{"webhook": "https://example.com"}],
            "Expected `'webhook'` to be a valid step notification",
            ".notify[0]",
            id="notify_webhook",
        ),
        param(
            [{"pagerduty_change_event": "pagerduty_change_event"}],
            "Expected `'pagerduty_change_event'` to be a valid step notification",
            ".notify[0]",
            id="notify_pagerduty",
        ),
        param(
            [{"slack": {"channels": []}}],
            "Expected `[]` to be non-empty",
            ".notify[0].slack.channels",
            id="notify_slack_empty",
            marks=UPSTREAM_SCHEMA_INVALID,
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
            marks=UPSTREAM_SCHEMA_INVALID,
        ),
        param(
            {"setup": {}},
            "Expected `{}` to be non-empty",
            ".matrix.setup",
            id="matrix_empty_setup",
            marks=UPSTREAM_SCHEMA_INVALID,
        ),
        param(
            {"setup": [""], "adjustments": [{"with": {"": ""}}]},
            "Expected `{'': ''}` to be of type `str`",
            ".matrix.adjustments[0].with",
            id="matrix_single_mismatched_adj",
            marks=UPSTREAM_SCHEMA_INVALID,
        ),
        param(
            {"setup": {"": []}, "adjustments": [{"with": []}]},
            "Expected `[]` to be of type `dict`",
            ".matrix.adjustments[0].with",
            id="matrix_multi_mismatched_adj",
        ),
        param(
            {"setup": [""], "adjustments": [{}]},
            # @TODO: "with" in message
            "Expected required fields `'with_value'` to be provided for model `ScalarAdjustment`",
            ".matrix.adjustments[0]",
            id="matrix_single_empty_adj",
        ),
        param(
            {"setup": {"a": ["b"]}, "adjustments": [{}]},
            # @TODO: "with" in message
            "Expected required fields `'with_value'` to be provided for model `MultiDimensionMatrixAdjustment`",
            ".matrix.adjustments[0]",
            id="matrix_multi_empty_adj",
        ),
        param(
            {"setup": {"": []}},
            "Expected key `''` to match regex `^[a-zA-Z0-9_]+$",
            ".matrix.setup",
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
            "Expected required fields `'trigger'` to be provided for model `TriggerStep`",
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
            {},
            "Expected required fields `'steps'` to be provided for model `GroupStep`",
            "",
            id="missing_steps",
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
            "Expected `'unknown'` to be a valid notification type",
            ".notify[0]",
            id="notify_unknown",
        ),
        param(
            [{"email": "hello@example.com"}],
            "Expected `'email'` to be a valid step notification",
            ".notify[0]",
            id="notify_email",
            marks=UPSTREAM_SCHEMA_INVALID,
        ),
        param(
            [{"webhook": "https://example.com"}],
            "Expected `'webhook'` to be a valid step notification",
            ".notify[0]",
            id="notify_webhook",
            marks=UPSTREAM_SCHEMA_INVALID,
        ),
        param(
            [{"pagerduty_change_event": "pagerduty_change_event"}],
            "Expected `'pagerduty_change_event'` to be a valid step notification",
            ".notify[0]",
            id="notify_pagerduty",
            marks=UPSTREAM_SCHEMA_INVALID,
        ),
        param(
            [{"slack": {"channels": []}}],
            "Expected `[]` to be non-empty",
            ".notify[0].slack.channels",
            id="notify_slack_empty",
            marks=UPSTREAM_SCHEMA_INVALID,
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
