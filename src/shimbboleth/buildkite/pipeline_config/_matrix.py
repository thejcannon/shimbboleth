# @TODO: Validate limits? https://buildkite.com/docs/pipelines/configure/workflows/build-matrix#matrix-limits
"""
Support for Command matrices.

See: https://buildkite.com/docs/pipelines/configure/step-types/command-step#matrix-attributes
"""

from typing import TypeAlias, Literal, Annotated

from shimbboleth.internal.clay.model import Model, field
from shimbboleth.internal.clay.validation import (
    MatchesRegex,
    NonEmptyList,
    Not,
    NonEmptyDict,
)
from shimbboleth.buildkite.pipeline_config._types import (
    skip_from_json,
    soft_fail_from_json,
    soft_fail_to_json,
)


MatrixElementT: TypeAlias = str | int | bool
MatrixArray: TypeAlias = list[MatrixElementT]


class _Adjustment(Model):
    # NB: Passing an empty string is equivalent to false.
    skip: bool | str = field(default=False, json_loader=skip_from_json)
    """Whether to skip this step or not. Passing a string provides a reason for skipping this command."""

    # NB: This differs from the upstream schema in that we "unpack"
    #  the `exit_status` object into the status.
    # @TODO: Upstream allows exit status to be 0...
    soft_fail: bool | NonEmptyList[Annotated[int, Not[Literal[0]]]] = field(
        default=False, json_loader=soft_fail_from_json, json_dumper=soft_fail_to_json
    )
    """Allow specified non-zero exit statuses not to fail the build."""


class SingleDimensionMatrix(Model, extra=False):
    """Configuration for single-dimension Build Matrix (e.g. list of elements/adjustments)."""

    class Adjustment(_Adjustment, extra=False):
        """An adjustment to a Build Matrix scalar element (e.g. single-dimension matrix)."""

        with_value: str = field(json_alias="with")
        """An existing (or new) element to adjust"""

    setup: NonEmptyList[MatrixElementT]

    adjustments: list[Adjustment] = field(default_factory=list)


class MultiDimensionMatrix(Model, extra=False):
    """Configuration for multi-dimension Build Matrix (e.g. map of elements/adjustments)."""

    class Adjustment(_Adjustment, Model):
        """An adjustment to a multi-dimension Build Matrix"""

        # @TODO: Each key in a `matrix.adjustments.with` must exist in the associated `matrix.setup`;
        #   new dimensions may not be created by an adjustment, only new elements; missing [...]
        # @TODO: Techincally, we could do the same MatchesRegex, but due to the above it's kind of pointless
        #   (but also this would be schema-invalid vs the above is logic-invalid)
        with_value: dict[str, MatrixElementT] = field(json_alias="with")
        """Specification of a new or existing Build Matrix combination"""

    setup: NonEmptyDict[
        Annotated[str, MatchesRegex(r"^[a-zA-Z0-9_]+$")], list[MatrixElementT]
    ]
    """Maps dimension names to a lists of elements"""

    adjustments: list[Adjustment] = field(default_factory=list)


@MultiDimensionMatrix._json_loader_("setup")
def _load_setup(
    value: NonEmptyDict[
        Annotated[str, MatchesRegex(r"^[a-zA-Z0-9_]+$")], str | list[MatrixElementT]
    ],
) -> NonEmptyDict[
    Annotated[str, MatchesRegex(r"^[a-zA-Z0-9_]+$")], list[MatrixElementT]
]:
    return {k: v if isinstance(v, list) else [v] for k, v in value.items()}
