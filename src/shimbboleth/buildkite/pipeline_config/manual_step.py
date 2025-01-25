from typing import Annotated, Literal
import re
from shimbboleth.internal.clay.model import field, Model
from shimbboleth.internal.clay.jsonT import JSONObject
from shimbboleth.internal.clay.validation import (
    NonEmptyList,
    MatchesRegex,
    ValidationError,
)
from shimbboleth.buildkite.pipeline_config._types import bool_from_json
from shimbboleth.buildkite.pipeline_config._types import list_str_from_json
from shimbboleth.buildkite.pipeline_config.step import Step


class _Option(Model):
    key: Annotated[str, MatchesRegex("^[a-zA-Z0-9-_]+$")]
    """The meta-data key that stores the field's input"""

    hint: str | None = None
    """The explanatory text that is shown after the label"""

    required: bool = field(default=True, json_loader=bool_from_json)
    """Whether the field is required for form submission"""


class _Select(_Option, extra=False):
    """
    For Input Step: https://buildkite.com/docs/pipelines/input-step#select-input-attributes
    For Block Step: https://buildkite.com/docs/pipelines/block-step#select-input-attributes
    """

    class Option(Model, extra=False):
        label: str
        """The text displayed on the select list item"""

        value: str
        """The value to be stored as meta-data"""

    select: str
    """The select input name"""

    options: NonEmptyList[Option]
    """The list of select field options."""


class ManualStep(Step, extra=False):
    """
    (The base of both Input and Block steps)
    """

    class Text(_Option, extra=False):
        """
        For Input Step: https://buildkite.com/docs/pipelines/input-step#text-input-attributes
        For Block Step: https://buildkite.com/docs/pipelines/block-step#text-input-attributes
        """

        text: str
        """The text input name"""

        default: str | None = None
        """The value that is pre-filled in the text field"""

        format: re.Pattern | None = None
        """A regular expression implicitly anchored to the beginning and end of the input and is functionally equivalent to the HTML5 pattern attribute."""

    class SingleSelect(_Select, extra=False):
        """A Select Option that only allows one option to be selected."""

        default: str | None = None
        """The value of the option that will be pre-selected in the dropdown"""

        multiple: Literal[False] = False
        """Whether more than one option may be selected"""

        def __init__(self, *, default: str | None = None, **kwargs):
            kwargs.pop("multiple", None)
            super().__init__(**kwargs)
            self.default = default
            self.multiple = False

    class MultiSelect(_Select, extra=False):
        """A Select Option that allows multiple options to be selected."""

        default: list[str] | None = None
        """The values of the options that will be pre-selected in the dropdown"""

        multiple: Literal[True]
        """Whether more than one option may be selected"""

        def __init__(self, *, default: list[str] | None = None, **kwargs):
            kwargs.pop("multiple", None)
            super().__init__(**kwargs)
            self.default = default
            self.multiple = True

    branches: list[str] = field(default_factory=list, json_loader=list_str_from_json)
    """Which branches will include this step in their builds"""

    fields: list[Text | SingleSelect | MultiSelect] = field(default_factory=list)
    """A list of input fields required to be filled out before unblocking the step"""

    prompt: str | None = None
    """The instructional message displayed in the dialog box when the unblock step is activated"""


@ManualStep.SingleSelect._json_loader_("multiple")
def _load_multiple_single(value: Literal[False, "false"]) -> Literal[False]:
    return False


@ManualStep.MultiSelect._json_loader_("multiple")
def _load_multiple_multi(value: Literal[True, "true"]) -> Literal[True]:
    return True


@ManualStep.MultiSelect._json_loader_("default")
def _load_default(value: str | list[str] | None) -> list[str] | None:
    if isinstance(value, str):
        return [value]
    return value


@ManualStep._json_loader_(
    "fields",
    json_schema_type=list[
        ManualStep.Text | ManualStep.SingleSelect | ManualStep.MultiSelect
    ],
)
def _load_fields(
    value: list[JSONObject],
) -> list[ManualStep.Text | ManualStep.SingleSelect | ManualStep.MultiSelect]:
    ret = []
    for index, field_dict in enumerate(value):
        with ValidationError.context(index=index):
            if "text" in field_dict:
                ret.append(ManualStep.Text.model_load(field_dict))
            elif "select" in field_dict:
                multiple = field_dict.pop("multiple", False)
                field_dict["multiple"] = multiple
                if multiple is True or multiple == "true":
                    ret.append(ManualStep.MultiSelect.model_load(field_dict))
                else:
                    ret.append(ManualStep.SingleSelect.model_load(field_dict))
            else:
                raise ValidationError(
                    value=field_dict,
                    expectation="contain `text` or `select`",
                )
    return ret
