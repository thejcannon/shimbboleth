from typing import ClassVar

from shimbboleth.internal.clay.model import Model, FieldAlias

from shimbboleth.buildkite.pipeline_config.block_step import BlockStep
from shimbboleth.buildkite.pipeline_config.input_step import InputStep
from shimbboleth.buildkite.pipeline_config.wait_step import WaitStep
from shimbboleth.buildkite.pipeline_config.trigger_step import TriggerStep
from shimbboleth.buildkite.pipeline_config.command_step import CommandStep


class NestedBlockStep(Model, extra=False):
    block: BlockStep

    # NB: No way to know if we should prepend or not, due to
    # https://forum.buildkite.community/t/ambiguity-of-type-manual-steps/4140
    manual: ClassVar = FieldAlias("block")


class NestedInputStep(Model, extra=False):
    input: InputStep


class NestedTriggerStep(Model, extra=False):
    trigger: TriggerStep


class NestedWaitStep(Model, extra=False):
    wait: WaitStep
    """Waits for previous steps to pass before continuing"""

    # @TODO: If both are given it gets mad about `waiter`.
    # But this actually looks like the discriminator
    # is choosing `WaitStep` over `NestedWaitStep`.
    waiter: ClassVar = FieldAlias("wait")


class NestedCommandStep(Model, extra=False):
    command: CommandStep

    commands: ClassVar = FieldAlias("command")
    script: ClassVar = FieldAlias("command")
