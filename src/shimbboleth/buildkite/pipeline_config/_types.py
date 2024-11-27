from typing_extensions import TypeAliasType
from pydantic import Field, BaseModel, WithJsonSchema

from typing import Any, Annotated, Literal

AgentsListT = TypeAliasType(
    "AgentsListT",
    Annotated[
        list[str],
        Field(
            description="Query rules to target specific agents in k=v format",
            examples=["queue=default", "xcode=true"],
        ),
    ],
)
AgentsObjectT = TypeAliasType(
    "AgentsObjectT",
    Annotated[
        # @TODO: Any?
        dict[str, Any],
        Field(
            description="Query rules to target specific agents",
            examples=[{"queue": "deploy"}, {"ruby": "2*"}],
        ),
    ],
)

AgentsT = TypeAliasType("AgentsT", AgentsObjectT | AgentsListT)
IfT = TypeAliasType(
    "IfT",
    Annotated[
        str,
        Field(
            description="A boolean expression that omits the step when false",
            examples=["build.message != 'skip me'", "build.branch == 'master'"],
        ),
    ],
)
# @TODO: RHS Any?
EnvT = TypeAliasType(
    "EnvT",
    Annotated[
        dict[str, Any],
        Field(
            description="Environment variables for this step",
            examples=[{"NODE_ENV": "test"}],
        ),
    ],
)
AllowDependencyFailureT = TypeAliasType(
    "AllowDependencyFailureT",
    Annotated[
        bool,
        Field(
            default=False,
            description="Whether to proceed with this step and further steps if a step named in the depends_on attribute fails",
        ),
    ],
)
BranchesT = TypeAliasType(
    "BranchesT",
    Annotated[
        str | list[str],
        Field(
            description="Which branches will include this step in their builds",
            examples=["master", ["feature/*", "chore/*"]],
        ),
    ],
)


class CacheMap(BaseModel):
    paths: str | list[str]

    name: str | None = None
    size: Annotated[str, Field(pattern="^\\d+g$")] | None = None


CacheT = TypeAliasType(
    "CacheT",
    Annotated[
        str | list[str] | CacheMap,
        Field(
            description="The paths for the caches to be used in the step",
            examples=[
                "dist/",
                [".build/*", "assets/*"],
                {
                    "name": "cool-cache",
                    "paths": ["/path/one", "/path/two"],
                    "size": "20g",
                },
            ],
        ),
    ],
)


class DependsOnDependency(BaseModel, extra="forbid"):
    allow_failure: bool | None = False
    step: str | None = None


DependsOnT = TypeAliasType(
    "DependsOnT",
    Annotated[
        None | str | list[str | DependsOnDependency],
        Field(description="The step keys for a step to depend on"),
    ],
)

UnblockFieldOptionT = TypeAliasType(
    "UnblockFieldOptionT",
    Annotated[dict[str, Any], Field(description="Option for an unblock field")],
)

UnblockFieldT = TypeAliasType(
    "UnblockFieldT",
    Annotated[
        dict[str, Any] | dict[str, Any],
        Field(description="A field in an unblock step"),
    ],
)

UnblockFieldsT = TypeAliasType(
    "UnblockFieldsT",
    Annotated[
        list[UnblockFieldT],
        Field(
            description="A list of input fields required to be filled out before unblocking the step"
        ),
    ],
)

LabelT = TypeAliasType(
    "LabelT",
    Annotated[
        str,
        Field(
            description="The label that will be displayed in the pipeline visualisation in Buildkite. Supports emoji.",
            examples=[":docker: Build"],
        ),
    ],
)

MatrixElementT = TypeAliasType(
    "MatrixElementT",
    Annotated[str | int | bool, Field(description="Matrix element value")],
)

PromptT = TypeAliasType(
    "PromptT",
    Annotated[
        str,
        Field(
            description="The instructional message displayed in the dialog box when the unblock step is activated",
            examples=["Release to production?"],
        ),
    ],
)

SkipT = TypeAliasType(
    "SkipT",
    Annotated[
        bool | str,
        Field(
            description="Whether this step should be skipped. You can specify a reason for using a string.",
            examples=[True, False, "My reason"],
        ),
    ],
)

BlockStepT = TypeAliasType(
    "BlockStepT",
    Annotated[
        Literal["block"],
        Field(
            description="Pauses the execution of a build and waits on a user to unblock it"
        ),
    ],
)

CancelOnBuildFailingT = TypeAliasType(
    "CancelOnBuildFailingT",
    Annotated[
        bool,
        Field(
            default=False,
            description="Whether to cancel the job as soon as the build is marked as failing",
        ),
    ],
)

InputStepT = TypeAliasType(
    "InputStepT",
    Annotated[
        Literal["input"],
        Field(
            description="Pauses the execution of a build and waits on a user to unblock it"
        ),
    ],
)

WaitStepT = TypeAliasType(
    "WaitStepT",
    Annotated[
        Literal["wait", "waiter"],
        Field(description="Waits for previous steps to pass before continuing"),
    ],
)

# @TODO: Make sure this works, Python-side
BoolLikeT = Annotated[
    bool | Literal["true", "false"],
    WithJsonSchema({"pattern": "^(true|false)$", "type": ["boolean", "string"]}),
]
