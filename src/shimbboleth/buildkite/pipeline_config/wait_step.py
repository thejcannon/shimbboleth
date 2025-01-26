from typing import ClassVar, Literal


from shimbboleth.internal.clay.model import FieldAlias, field

from shimbboleth.buildkite.pipeline_config.step import SubStep


class WaitStep(SubStep, extra=False):
    """
    A wait step waits for all previous steps to have successfully completed before allowing following jobs to continue.

    https://buildkite.com/docs/pipelines/wait-step
    """

    continue_on_failure: bool = field(default=False)
    """Continue to the next steps, even if the previous group of steps fail"""

    wait: str | None = None
    """Waits for previous steps to pass before continuing"""

    type: Literal["wait", "waiter"] = "wait"

    # (NB: These are somewhat meaningless, since they never appear in the UI)
    label: ClassVar = FieldAlias("wait", json_mode="prepend")
    name: ClassVar = FieldAlias("wait", json_mode="prepend")
