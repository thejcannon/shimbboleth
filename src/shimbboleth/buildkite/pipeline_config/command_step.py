from typing import Literal, Annotated, ClassVar

from shimbboleth.internal.clay.model import (
    Model,
    field,
    FieldAlias,
)
from shimbboleth.internal.clay.jsonT import JSONObject
from shimbboleth.internal.clay.validation import (
    Ge,
    Le,
    NonEmptyList,
    MatchesRegex,
)

from shimbboleth.buildkite.pipeline_config.step import Step
from shimbboleth.buildkite.pipeline_config._matrix import (
    MatrixArray,
    SingleDimensionMatrix,
    MultiDimensionMatrix,
)


class CommandStep(Step, extra=False):
    """
    A command step runs one or more shell commands on one or more agents.

    https://buildkite.com/docs/pipelines/command-step
    """

    class Cache(Model, extra=True):
        paths: list[str]

        name: str | None = None
        size: Annotated[str, MatchesRegex("^\\d+g$")] | None = None

    class Plugin(Model, extra=False):
        spec: str = field()
        """The plugin "spec". Usually in `<org>/<repo>#<tag>` format"""

        config: JSONObject | None = field(default=None)
        """The configuration to use (or None)"""

        # @FEAT: parse the spec and expose properties

        def model_dump(self) -> JSONObject:
            return {self.spec: self.config}

    class Retry(Model, extra=False):
        class Automatic(Model, extra=False):
            """See https://buildkite.com/docs/pipelines/configure/step-types/command-step#retry-attributes-automatic-retry-attributes"""

            exit_status: Literal["*"] | list[int] = field(default="*")
            """The exit status number that will cause this job to retry"""

            # @TODO: Upstram allows 0 (but not 11)
            limit: Annotated[int, Ge(1), Le(10)] | None = None
            """The number of times this job can be retried"""

            signal: str = "*"
            """The exit signal, that may be retried"""

            signal_reason: Literal[
                "*",
                "none",
                "agent_refused",
                "agent_stop",
                "cancel",
                "process_run_error",
                "signature_rejected",
            ] = "*"
            """The exit signal reason, that may be retried"""

        automatic: list[Automatic] = field(
            default_factory=lambda: [CommandStep.Retry.Automatic(limit=2)]
        )
        """When to allow a job to retry automatically"""

        class Manual(Model, extra=False):
            """See https://buildkite.com/docs/pipelines/configure/step-types/command-step#retry-attributes-manual-retry-attributes"""

            allowed: bool = field(default=True)
            """Whether or not this job can be retried manually"""

            permit_on_passed: bool = field(default=True)
            """Whether or not this job can be retried after it has passed"""

            reason: str | None = None
            """
            A string that will be displayed in a tooltip on the Retry button in Buildkite.

            This will only be displayed if the `allowed` attribute is set to false.
            """

        manual: Manual = field(
            default_factory=lambda: CommandStep.Retry.Manual(allowed=True)
        )
        """When to allow a job to be retried manually"""

    class Signature(Model, extra=True):
        """The signature of the command step, generally injected by agents at pipeline upload time"""

        algorithm: str | None = None
        """The algorithm used to generate the signature"""

        signed_fields: list[str] = field(default_factory=list)
        """The fields that were signed to form the signature value"""

        value: str | None = None
        """The signature value, a JWS compact signature with a detached body"""

    agents: dict[str, str] = field(default_factory=dict)
    """
    Query rules to target specific agents.

    See https://buildkite.com/docs/agent/v3/cli-start#agent-targeting
    """

    artifact_paths: list[str] = field(default_factory=list)
    """The glob paths of artifacts to upload once this step has finished running"""

    branches: list[str] = field(default_factory=list)
    """Which branches will include this step in their builds"""

    cache: Cache = field(default_factory=lambda: CommandStep.Cache(paths=[]))
    """See: https://buildkite.com/docs/pipelines/hosted-agents/linux"""

    cancel_on_build_failing: bool = field(default=False)
    """Whether to cancel the job as soon as the build is marked as failing"""

    command: list[str] = field(default_factory=list)
    """The commands to run on the agent"""

    concurrency: int | None = None
    """
    The maximum number of jobs created from this step that are allowed to run at the same time.

    If you use this attribute, you must also define concurrency_group.
    """

    concurrency_group: str | None = None
    """A unique name for the concurrency group that you are creating with the concurrency attribute"""

    concurrency_method: Literal["ordered", "eager"] | None = None
    """
    Control command order, allowed values are 'ordered' (default) and 'eager'.

    If you use this attribute, you must also define concurrency_group and concurrency."""

    env: dict[str, str] = field(default_factory=dict)
    """Environment variables for this step"""

    label: str | None = None
    """The label that will be displayed in the pipeline visualization in Buildkite. Supports emoji."""

    matrix: MatrixArray | SingleDimensionMatrix | MultiDimensionMatrix | None = None
    """
    Matrix expansions for this step.

    See https://buildkite.com/docs/pipelines/configure/workflows/build-matrix
    """

    notify: list[Step.NotifyT] = field(default_factory=list)
    """Array of notification options for this step"""

    parallelism: int | None = None
    """The number of parallel jobs that will be created based on this step"""

    # NB: We use a list of plugins, since the same plugin can appear multiple times
    plugins: list[Plugin] = field(default_factory=list)
    """An array of plugins for this step."""

    priority: int | None = None
    """Priority of the job, higher priorities are assigned to agents"""

    retry: Retry | None = None
    """The conditions for retrying this step."""

    signature: Signature | None = None
    """@TODO (missing description)"""

    # NB: Passing an empty string is equivalent to false.
    skip: bool | str = field(default=False)
    """Whether to skip this step or not. Passing a string provides a reason for skipping this command."""

    # NB: This differs from the upstream schema in that we "unpack"
    #  the `exit_status` object into the status.
    soft_fail: bool | NonEmptyList[int] = field(default=False)
    """Allow specified non-zero exit statuses not to fail the build."""

    # @TODO: Zero is OK upstream?
    timeout_in_minutes: Annotated[int, Ge(1)] | None = None
    """The number of minutes to time out a job"""

    type: Literal["script", "command", "commands"] = "command"

    name: ClassVar = FieldAlias("label", json_mode="prepend")
    commands: ClassVar = FieldAlias("command")

    def __post_init__(self):
        # @TODO: Verify the concurrency_group fields (together)
        pass
