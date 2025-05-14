from typing import ClassVar, Literal


from shimbboleth.internal.clay.jsonT import JSON
from shimbboleth.internal.clay.model import FieldAlias
from shimbboleth.buildkite.pipeline_config._types import BKBool
from shimbboleth.buildkite.pipeline_config.step import SubStep


class WaitStep(SubStep, extra=False):
    """
    A wait step waits for all previous steps to have successfully completed before allowing following jobs to continue.

    https://buildkite.com/docs/pipelines/wait-step
    """

    continue_on_failure: BKBool = BKBool(default=False)
    """Continue to the next steps, even if the previous group of steps fail"""

    # NB: Can be literally anything, since its ignored
    wait: JSON = None

    # NB: We don't canonicalize this, in case someone is using this
    #   to encode information.
    type: Literal["wait", "waiter"] = "wait"

    # (NB: These are somewhat meaningless, since they never appear in the UI)
    label: ClassVar = FieldAlias("wait", json_mode="prepend")
    name: ClassVar = FieldAlias("wait", json_mode="prepend")

fields = WaitStep.__dataclass_fields__
print(fields)
