import pytest
from pytest import param

from shimbboleth.buildkite.pipeline_config import BuildkitePipeline, GroupStep, WaitStep
from shimbboleth.buildkite.pipeline_config.tests.conftest import (
    STEP_TYPE_PARAMS,
    SKIP_VALS,
)
from shimbboleth.buildkite.pipeline_config.tests.test_schema_valid_pipelines import (
    StepTestBase,
    BASECAMP_CAMPFIRE_URL,
)


@pytest.mark.parametrize("steptype_param", [STEP_TYPE_PARAMS["group"]])
@pytest.mark.parametrize(
    "step",
    [
        param({"group": "group", "label": "label", "steps": ["wait"]}, id="label"),
        param({"group": "group", "name": "name", "steps": ["wait"]}, id="name"),
        param({"group": "group", "label": "label", "name": "name", "steps": ["wait"]}, id="label_and_name"),
        param(
            {
                "group": "group",
                "notify": [
                    "github_check",
                    "github_commit_status",
                    {"basecamp_campfire": BASECAMP_CAMPFIRE_URL},
                    {"slack": "#general"},
                    {"slack": {"channels": ["#general"]}},
                    {"slack": {"channels": ["#general"], "message": "message"}},
                    {"github_commit_status": {"context": "context"}},
                    {"github_check": {"name": "name"}},
                ],
                "steps": ["wait"]
            },
            id="notify",
        ),
        *[param({"group": "group", "skip": value, "steps": ["wait"]}, id=f"skip_{value}") for value in SKIP_VALS],
        param({"group": "group", "steps": ["wait"]}, id="steps_single"),
        param({"group": "group", "steps": ["wait", "wait"]}, id="steps_multiple"),
    ],
)
class Test_GroupStep(StepTestBase):
    pass