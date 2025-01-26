"""
This module attaches all the JSON loaders (and dumpers) to the models.

(It gets loaded at the end of `__init__.py` so we know they are sure to get attached)

It handles all the nice "wide" types that Buildkite supports, like `str | list[str]` and
narrows them down to the specific types that the models expect (like `list[str]`).
"""
# Slaps roof of module - This baby can fit so much JSON in it.

from typing import (
    Any,
    Literal,
    ClassVar,
    Annotated,
    cast,
)

from shimbboleth.buildkite.pipeline_config import BuildkitePipeline
from shimbboleth.internal.clay.model import Model, FieldAlias
from shimbboleth.internal.clay.jsonT import JSONObject
from shimbboleth.internal.clay.validation import (
    ValidationError,
    NonEmptyList,
    Not,
    SingleKeyDict,
    NonEmptyDict,
    MatchesRegex,
)
from shimbboleth.buildkite.pipeline_config.block_step import BlockStep
from shimbboleth.buildkite.pipeline_config.input_step import InputStep
from shimbboleth.buildkite.pipeline_config.wait_step import WaitStep
from shimbboleth.buildkite.pipeline_config.step import Step, SubStep
from shimbboleth.buildkite.pipeline_config.notify import Notify
from shimbboleth.buildkite.pipeline_config.trigger_step import TriggerStep
from shimbboleth.buildkite.pipeline_config.command_step import CommandStep
from shimbboleth.buildkite.pipeline_config.manual_step import ManualStep
from shimbboleth.buildkite.pipeline_config._utils import rubystr
from shimbboleth.buildkite.pipeline_config.group_step import GroupStep


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


# ===== (Utilities) =====


class ExitStatus(Model, extra=True):
    exit_status: Literal["*"] | int
    """The exit status number that will cause this job to soft-fail"""


def parse_step(
    step: Any,
) -> BlockStep | InputStep | CommandStep | WaitStep | TriggerStep | GroupStep:
    if isinstance(step, str):
        if step in ("block", "manual"):
            return BlockStep(type=step)
        elif step == "input":
            return InputStep(type=step)
        elif step in ("command", "commands", "script"):
            return CommandStep(type=step)
        elif step == "wait" or step == "waiter":
            return WaitStep(type=step)

    elif isinstance(step, dict):
        # @TODO: Ensure keys are strings?
        for stepkey, nestedmodel, stepmodel in (
            ("block", NestedBlockStep, BlockStep),
            ("manual", NestedBlockStep, BlockStep),
            ("input", NestedInputStep, InputStep),
            ("trigger", NestedTriggerStep, TriggerStep),
            ("wait", NestedWaitStep, WaitStep),
            ("waiter", NestedWaitStep, WaitStep),
            ("command", NestedCommandStep, CommandStep),
            ("commands", NestedCommandStep, CommandStep),
            ("script", NestedCommandStep, CommandStep),
            ("group", None, GroupStep),
        ):
            if stepkey in step:
                if isinstance(step[stepkey], dict) and nestedmodel:
                    return getattr(nestedmodel.model_load(step), stepkey)
                return stepmodel.model_load(step)

            if step.get("type", None) == stepkey:
                return stepmodel.model_load(step)

    raise ValidationError(value=step, expectation="be a valid Buildkite pipeline step")


def load_str_list(value: str | list[str]) -> list[str]:
    return value if isinstance(value, list) else [value]


def load_bool(value: bool | Literal["true", "false"]) -> bool:
    return value in (True, "true")


def load_skip(value: str | bool) -> str | bool:
    if value in (True, False, "true", "false"):
        return load_bool(value)
    if value == "":
        return False
    return value


def load_soft_fail(
    value: bool | Literal["true", "false"] | list[ExitStatus],
) -> bool | NonEmptyList[int]:
    if value in (True, "true"):
        return True
    elif value in (False, "false"):
        return False
    elif value == []:
        return False
    elif any(wrapped.exit_status == "*" for wrapped in value):
        return True
    return [cast(int, wrapped.exit_status) for wrapped in value]


def dump_soft_fail(
    value: bool | NonEmptyList[Annotated[int, Not[Literal[0]]]],
) -> bool | list[dict[str, int]]:
    if isinstance(value, bool):
        return value
    return [{"exit_status": exit_status} for exit_status in value]


# ===== BuildkitePipeline =====


# @TODO: "list[str]" seems to just ignore non-strings? (on command)
# @TODO: BK stores things in "k=v" format. What if there's duplicate keys?
#   Oh God, I think they just pass those right along...
@BuildkitePipeline._json_loader_("agents")
def load_agents(value: list[str] | JSONObject) -> dict[str, str]:
    if isinstance(value, list):
        # @TODO: ignore non-strings
        return dict(
            (elem.split("=", 1) if "=" in elem else (elem, "true")) for elem in value
        )
    return {k: rubystr(v) for k, v in value.items() if v is not None}


@BuildkitePipeline._json_loader_(
    "steps",
    json_schema_type=list[
        BlockStep
        | InputStep
        | CommandStep
        | WaitStep
        | TriggerStep
        | GroupStep
        | NestedWaitStep
        | NestedInputStep
        | NestedBlockStep
        | NestedCommandStep
        | NestedTriggerStep
        | Literal[
            "block",
            "manual",
            "input",
            "command",
            "commands",
            "script",
            "wait",
            "waiter",
        ]
    ],
)
def load_steps(
    value: list[str | JSONObject],
) -> list[BlockStep | InputStep | CommandStep | WaitStep | TriggerStep | GroupStep]:
    ret = []
    for index, step in enumerate(value):
        with ValidationError.context(index=index):
            ret.append(parse_step(step))
    return ret


@BuildkitePipeline._json_loader_("env")
def _(
    # NB: Unlike Command steps, invalid value types aren't allowed
    value: dict[str, str | int | bool],
) -> dict[str, str]:
    return {k: rubystr(v) for k, v in value.items()}


@BuildkitePipeline._json_loader_(
    "notify",
    json_schema_type=list[
        Literal["github_check", "github_commit_status"] | BuildkitePipeline.NotifyT
    ],
)
def _(
    value: list[str | JSONObject],
) -> list[BuildkitePipeline.NotifyT]:
    from shimbboleth.buildkite.pipeline_config.notify import _parse_notify

    ret = []
    for index, elem in enumerate(value):
        with ValidationError.context(index=index):
            ret.append(_parse_notify(elem))
    return ret

# ===== Notify =====


@Notify.Slack._json_loader_("info")
def _load_slack(value: str | Notify.Slack.Info) -> Notify.Slack.Info:
    if isinstance(value, str):
        return Notify.Slack.Info.model_load({"channels": [value]})
    return value

# ===== Step =====

Step.Dependency._json_loader_("allow_failure")(load_bool)
Step._json_loader_("allow_dependency_failure")(load_bool)


@Step._json_loader_("depends_on", json_schema_type=str | list[str | Step.Dependency])
@staticmethod
def _(value: str | list[str | JSONObject]) -> list[Step.Dependency]:
    if isinstance(value, str):
        return [Step.Dependency(step=value)]
    ret = []
    for index, elem in enumerate(value):
        with ValidationError.context(index=index):
            ret.append(
                Step.Dependency(step=elem)
                if isinstance(elem, str)
                else Step.Dependency.model_load(elem)
            )
    return ret

SubStep._json_loader_("branches")(load_str_list)

# ===== CommandStep ====

CommandStep._json_loader_("artifact_paths")(load_str_list)
CommandStep._json_loader_("cancel_on_build_failing")(load_bool)
CommandStep._json_loader_("command")(load_str_list)
CommandStep._json_loader_("skip")(load_skip)
CommandStep._json_loader_("soft_fail")(load_soft_fail)
CommandStep._json_dumper_("soft_fail")(dump_soft_fail)
CommandStep.Matrix.SingleDim.Adjustment._json_loader_("skip")(load_skip)
assert (
    CommandStep.Matrix.MultiDim.Adjustment.__dataclass_fields__["skip"].metadata[
        "json_loader"
    ]
    == load_skip
)
CommandStep.Matrix.SingleDim.Adjustment._json_loader_("soft_fail")(load_soft_fail)
CommandStep.Matrix.SingleDim.Adjustment._json_dumper_("soft_fail")(dump_soft_fail)
assert (
    CommandStep.Matrix.MultiDim.Adjustment.__dataclass_fields__["soft_fail"].metadata[
        "json_loader"
    ]
    == load_soft_fail
)
assert (
    CommandStep.Matrix.MultiDim.Adjustment.__dataclass_fields__["soft_fail"].metadata[
        "json_dumper"
    ]
    == dump_soft_fail
)


# @TODO: If there is no difference, just double-decorate above, otherwise whats the difference?
@CommandStep._json_loader_("agents")
def _(value: list[str] | JSONObject) -> dict[str, str]:
    return load_agents(value)


@CommandStep._json_loader_("cache")
def _(value: str | list[str] | CommandStep.Cache) -> CommandStep.Cache:
    if isinstance(value, str):
        return CommandStep.Cache(paths=[value])
    if isinstance(value, list):
        return CommandStep.Cache(paths=value)
    return value


@CommandStep._json_loader_("env")
def _(
    # @TODO: Upstream allows value to be anything and ignores non-dict. WTF
    value: JSONObject,
) -> dict[str, str]:
    return {
        k: rubystr(v)
        for k, v in value.items()
        # NB: Upstream just ignores invalid types
        if isinstance(v, (str, int, bool))
    }


@CommandStep._json_loader_("matrix", json_schema_type="return")
def _(
    value: CommandStep.Matrix.Array | JSONObject | None,
) -> (
    CommandStep.Matrix.Array
    | CommandStep.Matrix.SingleDim
    | CommandStep.Matrix.MultiDim
    | None
):
    if value is None:
        return None
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        if isinstance(value["setup"], list):
            return CommandStep.Matrix.SingleDim.model_load(value)
        return CommandStep.Matrix.MultiDim.model_load(value)

    # @TODO: Error on wrong type


@CommandStep.Matrix.MultiDim._json_loader_("setup")
def _load_setup(
    value: NonEmptyDict[
        Annotated[str, MatchesRegex(r"^[a-zA-Z0-9_]+$")],
        str | list[CommandStep.Matrix.ElementT],
    ],
) -> NonEmptyDict[
    Annotated[str, MatchesRegex(r"^[a-zA-Z0-9_]+$")], list[CommandStep.Matrix.ElementT]
]:
    return {k: v if isinstance(v, list) else [v] for k, v in value.items()}


@CommandStep._json_loader_(
    "notify",
    json_schema_type=list[
        Literal["github_check", "github_commit_status"] | Step.NotifyT
    ],
)
def _(value: list[str | JSONObject]) -> list[Step.NotifyT]:
    return CommandStep._parse_notify(value)


@CommandStep._json_loader_("plugins")
def _(
    value: dict[str, JSONObject | None]
    | list[str | SingleKeyDict[str, JSONObject | None]],
) -> list[CommandStep.Plugin]:
    if isinstance(value, dict):
        return [
            CommandStep.Plugin(spec=spec, config=config)
            for spec, config in value.items()
        ]
    ret = []
    for index, elem in enumerate(value):
        if isinstance(elem, str):
            ret.append(CommandStep.Plugin(spec=elem, config=None))
        else:
            # NB: Because we aren't _assigning_ to a 'SingleKeyDict`, the validation doesn't
            #   kick in. (Womp Womp)
            if len(elem) > 1:
                raise ValidationError(
                    elem, expectation="have only one key", index=index
                )
            spec, config = next(iter(elem.items()))
            ret.append(CommandStep.Plugin(spec=spec, config=config))
    return ret


# ===== CommandStep.Retry =====


@CommandStep.Retry._json_loader_("automatic")
def _(
    value: bool
    | Literal["true", "false"]
    | CommandStep.Retry.Automatic
    | list[CommandStep.Retry.Automatic],
) -> list[CommandStep.Retry.Automatic]:
    if value in (False, "false"):
        return []
    elif value in (True, "true"):
        return [CommandStep.Retry.Automatic(limit=2)]
    elif isinstance(value, CommandStep.Retry.Automatic):
        return [value]
    return value


@CommandStep.Retry.Automatic._json_loader_("exit_status")
def _(
    value: Literal["*"] | int | list[int],
) -> Literal["*"] | list[int]:
    if isinstance(value, int):
        return [value]
    if value == "*":
        return value
    return value


@CommandStep.Retry._json_loader_("manual")
def _(
    value: bool | Literal["true", "false"] | CommandStep.Retry.Manual,
) -> CommandStep.Retry.Manual:
    if value in (False, "false"):
        return CommandStep.Retry.Manual(allowed=False)
    elif value in (True, "true"):
        return CommandStep.Retry.Manual(allowed=True)
    return value


CommandStep.Retry.Manual._json_loader_("allowed")(load_bool)
CommandStep.Retry.Manual._json_loader_("permit_on_passed")(load_bool)

# ===== ManualStep =====

ManualStep.Text._json_loader_("required")(load_bool)
assert (
    ManualStep.SingleSelect.__dataclass_fields__["required"].metadata["json_loader"]
    == load_bool
)
assert (
    ManualStep.MultiSelect.__dataclass_fields__["required"].metadata["json_loader"]
    == load_bool
)


@ManualStep.SingleSelect._json_loader_("multiple")
def _(value: Literal[False, "false"]) -> Literal[False]:
    return False


@ManualStep.MultiSelect._json_loader_("multiple")
def _(value: Literal[True, "true"]) -> Literal[True]:
    return True


@ManualStep.MultiSelect._json_loader_("default")
def _(value: str | list[str] | None) -> list[str] | None:
    if isinstance(value, str):
        return [value]
    return value


@ManualStep._json_loader_("fields", json_schema_type="return")
def _(
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


# ===== GroupStep =====

GroupStep._json_loader_("skip")(load_skip)


@GroupStep._json_loader_(
    "steps",
    json_schema_type=NonEmptyList[
        BlockStep
        | InputStep
        | CommandStep
        | WaitStep
        | TriggerStep
        | NestedWaitStep
        | NestedInputStep
        | NestedBlockStep
        | NestedCommandStep
        | NestedTriggerStep
        | Literal[
            "block",
            "manual",
            "input",
            "command",
            "commands",
            "script",
            "wait",
            "waiter",
        ]
    ],
)
def _(
    value: list[str | JSONObject],
) -> NonEmptyList[BlockStep | InputStep | CommandStep | WaitStep | TriggerStep]:
    # @TODO: Don't allow group steps in here
    return load_steps(value)  # type: ignore


@GroupStep._json_loader_(
    "notify",
    json_schema_type=list[
        Literal["github_check", "github_commit_status"] | Step.NotifyT
    ],
)
def _(value: list[str | JSONObject]) -> list[Step.NotifyT]:
    return GroupStep._parse_notify(value)


# ===== TriggerStep =====

TriggerStep._json_loader_("is_async")(load_bool)
TriggerStep._json_loader_("skip")(load_skip)
TriggerStep._json_loader_("soft_fail")(load_bool)

# ===== WaitStep =====

WaitStep._json_loader_("continue_on_failure")(load_bool)
