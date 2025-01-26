from typing import ClassVar


from shimbboleth.internal.clay.model import field, FieldAlias
from shimbboleth.internal.clay.validation import NonEmptyList
from shimbboleth.buildkite.pipeline_config.block_step import BlockStep
from shimbboleth.buildkite.pipeline_config.input_step import InputStep
from shimbboleth.buildkite.pipeline_config.wait_step import WaitStep
from shimbboleth.buildkite.pipeline_config.trigger_step import TriggerStep
from shimbboleth.buildkite.pipeline_config.command_step import CommandStep
from shimbboleth.buildkite.pipeline_config.step import Step


class GroupStep(Step, extra=False):
    """
    A group step can contain various sub-steps, and display them in a single logical group on the Build page.

    https://buildkite.com/docs/pipelines/group-step
    """

    # NB: `group` is required, but can be null.
    # (e.g. BK complains about `steps: [{"steps": ["wait"]}]` not having a type)
    group: str | None
    """The name to give to this group of steps"""

    notify: list[Step.NotifyT] = field(default_factory=list)
    """Array of notification options for this step"""

    # NB: Passing an empty string is equivalent to false.
    skip: bool | str = field(default=False)
    "Whether this step should be skipped. Passing a string provides a reason for skipping this command"

    steps: NonEmptyList[
        BlockStep | InputStep | CommandStep | WaitStep | TriggerStep
    ] = field()
    """A list of steps"""

    name: ClassVar = FieldAlias("group", json_mode="append")
    label: ClassVar = FieldAlias("group", json_mode="append")
