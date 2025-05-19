from typing import Literal

from shimbboleth.buildkite.pipeline_config._converters import bk_bool
from shimbboleth.buildkite.pipeline_config.step import SubStep
from shimbboleth.internal.clay.jsonT import JSON
from shimbboleth.internal.clay.model import field


class WaitAlias:
    def __get__(self, instance, owner):
        if instance is None:
            return None
        return instance.wait

    def __set__(self, instance, value: JSON):
        if value is None:
            return
        instance.wait = value

class WaitStep(SubStep, extra=False):
    """
    A wait step waits for all previous steps to have successfully completed before allowing following jobs to continue.

    https://buildkite.com/docs/pipelines/wait-step
    """

    continue_on_failure: bool = field(default=False, converter=bk_bool(default=False))
    """Continue to the next steps, even if the previous group of steps fail"""

    # NB: Can be literally anything, since its ignored
    wait: JSON = None

    # NB: We don't canonicalize this, in case someone is using this
    #   to encode information.
    type: Literal["wait", "waiter"] = "wait"

    # (NB: These are somewhat meaningless, since they never appear in the UI)
    label: JSON = WaitAlias()
    name: JSON = WaitAlias()
