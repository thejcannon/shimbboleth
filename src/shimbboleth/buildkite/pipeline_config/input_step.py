from typing import Literal
from typing_extensions import ClassVar

from shimbboleth.internal.clay.model import FieldAlias
from shimbboleth.buildkite.pipeline_config.manual_step import ManualStep, field


class InputStep(ManualStep, extra=False):
    """
    An input step is used to collect information from a user.

    https://buildkite.com/docs/pipelines/input-step
    """

    input: str | None = field(default=None)
    """The label of the input step"""

    type: Literal["input"] = "input"

    label: ClassVar = FieldAlias("input", json_mode="prepend")
    name: ClassVar = FieldAlias("input", json_mode="prepend")
