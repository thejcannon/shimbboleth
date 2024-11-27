from typing import Annotated

from pydantic import BaseModel, Field

from ._types import AgentsT, EnvT
from ._block_step import BlockStep, NestedBlockStep, StringBlockStep
from ._input_step import InputStep, NestedInputStep, StringInputStep
from ._wait_step import WaitStep, NestedWaitStep, StringWaitStep
from ._trigger_step import TriggerStep, NestedTriggerStep
from ._command_step import CommandStep, NestedCommandStep
from ._group_step import GroupStep
from ._notify import BuildNotifyT


class BuildkitePipeline(BaseModel):
    steps: Annotated[
        list[
            BlockStep
            | NestedBlockStep
            | StringBlockStep
            | InputStep
            | NestedInputStep
            | StringInputStep
            | CommandStep
            | NestedCommandStep
            | WaitStep
            | NestedWaitStep
            | StringWaitStep
            | TriggerStep
            | NestedTriggerStep
            | GroupStep
        ],
        Field(description="A list of steps"),
    ]

    agents: AgentsT | None = None
    env: EnvT | None = None
    notify: BuildNotifyT | None = None