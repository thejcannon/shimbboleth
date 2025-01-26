from typing import cast
from functools import lru_cache


from shimbboleth.internal.clay.model import Model, field
from shimbboleth.internal.clay.jsonT import JSONArray, JSONObject
from shimbboleth.internal.clay.validation import ValidationError

from shimbboleth.buildkite.pipeline_config.block_step import BlockStep
from shimbboleth.buildkite.pipeline_config.input_step import InputStep
from shimbboleth.buildkite.pipeline_config.wait_step import WaitStep
from shimbboleth.buildkite.pipeline_config.trigger_step import TriggerStep
from shimbboleth.buildkite.pipeline_config.command_step import CommandStep
from shimbboleth.buildkite.pipeline_config.group_step import GroupStep
from shimbboleth.buildkite.pipeline_config.notify import Notify


ALL_STEP_TYPES = (
    BlockStep,
    InputStep,
    CommandStep,
    WaitStep,
    TriggerStep,
    GroupStep,
)

ALL_SUBSTEP_TYPES = (
    BlockStep,
    InputStep,
    CommandStep,
    WaitStep,
    TriggerStep,
)


@lru_cache(maxsize=1)
def get_schema():
    schema = BuildkitePipeline.model_json_schema
    pipeline_schema = schema.copy()
    defs = cast(JSONObject, pipeline_schema.pop("$defs"))
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "oneOf": [
            {"$ref": "#/$defs/pipeline"},
            {"$ref": "#/$defs/pipeline/properties/steps"},
        ],
        "$defs": {
            "pipeline": pipeline_schema,
            **defs,
        },
    }


class BuildkitePipeline(Model, extra=True):
    steps: list[
        BlockStep | InputStep | CommandStep | WaitStep | TriggerStep | GroupStep
    ] = field()
    """A list of steps"""

    agents: dict[str, str] = field(default_factory=dict)
    """
    Query rules to target specific agents.

    See https://buildkite.com/docs/agent/v3/cli-start#agent-targeting
    """

    env: dict[str, str] = field(default_factory=dict)
    """Environment variables for this pipeline"""

    NotifyT = (
        Notify.Email
        | Notify.BasecampCampfire
        | Notify.Slack
        | Notify.Webhook
        | Notify.Pagerduty
        | Notify.GitHubCheck
        | Notify.GitHubCommitStatus
    )

    notify: list[NotifyT] = field(default_factory=list)
    """
    List of services to notify.

    See https://buildkite.com/docs/pipelines/configure/notifications
    """

    # @TODO: Missing cache? https://buildkite.com/docs/pipelines/hosted-agents/linux#cache-volumes

    @classmethod
    def model_load(cls, value: JSONArray | JSONObject):
        # NB: Handle "list of steps" as a pipeline
        if isinstance(value, list):
            try:
                return super().model_load({"steps": value})
            except ValidationError as e:
                e.path.pop(0)  # Remove the "steps"
                raise
        return super().model_load(value)


# NB: import this at the enc. See the module docsting for more info.
import shimbboleth.buildkite.pipeline_config._json_compat  # noqa: E402, F401
