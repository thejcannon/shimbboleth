# @TODO: Split this up (also conftest is eww, maybe just use vanilla python?)
import pytest
import httpx
import os
from dataclasses import dataclass
from typing import TypeVar, Generic, Any

from shimbboleth.buildkite.pipeline_config.tests.cached_bk_api import CachedAPITransport
from shimbboleth.buildkite.pipeline_config import (
    BlockStep,
    InputStep,
    CommandStep,
    WaitStep,
    TriggerStep,
    GroupStep,
    get_schema,
)
from shimbboleth.internal.clay.model import Model
import jsonschema


ModelT = TypeVar("ModelT", bound=Model)

UPSTREAM_JSON_SCHEMA_COMMIT = "2fbbfc199bd66c0ff64303a2d9c7072ad24f3ce3"
UPSTREAM_JSON_SCHEMA_URL = f"https://raw.githubusercontent.com/buildkite/pipeline-schema/{UPSTREAM_JSON_SCHEMA_COMMIT}/schema.json"


@dataclass(slots=True, frozen=True)
class StepTypeParam(Generic[ModelT]):
    cls: type[ModelT]
    ctor_defaults: dict[str, Any]

    @property
    def stepname(self) -> str:
        return self.cls.__name__.lower().removesuffix("step")

    def ctor(self, **kwargs) -> ModelT:
        return self.cls(**{**kwargs, **self.ctor_defaults})

    def model_load(self, value: dict[str, Any]) -> ModelT:
        return self.cls.model_load({**value, **self.dumped_default})

    @property
    def dumped_default(self) -> dict[str, Any]:
        return self.ctor().model_dump()

    @property
    def type(self) -> str:
        return self.ctor_defaults["type"]


STEP_TYPE_PARAMS = {
    "block": pytest.param(StepTypeParam(BlockStep, {"type": "block"}), id="block"),
    "command": pytest.param(
        StepTypeParam(CommandStep, {"type": "command"}), id="command"
    ),
    "input": pytest.param(StepTypeParam(InputStep, {"type": "input"}), id="input"),
    "wait": pytest.param(StepTypeParam(WaitStep, {"type": "wait"}), id="wait"),
    "trigger": pytest.param(
        StepTypeParam(TriggerStep, {"type": "trigger", "trigger": "trigger"}),
        id="trigger",
    ),
    "group": pytest.param(
        StepTypeParam(GroupStep, {"group": "group", "steps": [WaitStep()]}), id="group"
    ),
}
ALL_STEP_TYPE_PARAMS = [
    step_type_param for step_type_param in STEP_TYPE_PARAMS.values()
]
ALL_SUBSTEP_TYPE_PARAMS = [
    step_type_param
    for step_type_param in STEP_TYPE_PARAMS.values()
    if step_type_param.id != "group"
]

# === Fixtures ===


@pytest.fixture(params=ALL_STEP_TYPE_PARAMS)
def all_step_types(request) -> StepTypeParam:
    return request.param


@pytest.fixture(params=ALL_SUBSTEP_TYPE_PARAMS)
def all_substep_types(request) -> StepTypeParam:
    return request.param


@pytest.fixture(scope="session")
def generated_schema():
    return jsonschema.Draft202012Validator(
        get_schema(), format_checker=jsonschema.Draft202012Validator.FORMAT_CHECKER
    )


# NB: Technically because of the caching this fixture is cache-scoped
@pytest.fixture(scope="session")
def upstream_schema(pytestconfig) -> jsonschema.Draft202012Validator:
    cache_key = f"BKSchema/schema.{UPSTREAM_JSON_SCHEMA_COMMIT}.json"
    schema = pytestconfig.cache.get(cache_key, None)
    if not schema:
        response = httpx.get(UPSTREAM_JSON_SCHEMA_URL)
        response.raise_for_status()
        schema = response.json()
        pytestconfig.cache.set(cache_key, schema)

    return jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.Draft202012Validator.FORMAT_CHECKER
    )


@pytest.fixture(scope="session")
def cached_bk_api(pytestconfig: pytest.Config):
    """
    Fixture for a `httpx.Client` around the Buildkite API, which caches responses.
    """
    # @TODO: Can we mark as integration if the token isn't set?

    return httpx.Client(
        base_url="https://api.buildkite.com/v2/",
        headers={"Authorization": f"Bearer {os.environ['BK_PIPELINE_API_TOKEN']}"},
        transport=CachedAPITransport(pytestconfig.cache),
    )
    # @TODO: Cache the results in the GitHub Actions workflow?
