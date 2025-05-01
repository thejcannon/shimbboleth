from shimbboleth.buildkite.pipeline_config.wait_step import WaitStep
import pytest
from pytest import param
from typing import Any, Callable
from shimbboleth.buildkite.pipeline_config.tests2.helpers import (
    get_upstream_schema,
    get_generated_schema,
    is_valid_upstream,
)


IsValidPipeline = Callable[[dict[str, Any]], bool]


def _try_model_load(step_data: dict[str, Any]) -> bool:
    try:
        WaitStep.model_load(step_data)
    except Exception:
        return False
    return True


def _try_generated_json_schema(step_data: dict[str, Any]) -> bool:
    return get_generated_schema().is_valid({"steps": [step_data]})


def _try_upstream_json_schema(step_data: dict[str, Any]) -> bool:
    return get_upstream_schema().is_valid({"steps": [step_data]})


def _try_upstream_api(step_data: dict[str, Any]) -> bool:
    return is_valid_upstream({"steps": [step_data]})


valid_pipeline_test = pytest.mark.parametrize(
    "is_valid_pipeline",
    [
        param(_try_model_load, id="model_load"),
        param(_try_generated_json_schema, id="generated_json_schema"),
        param(_try_upstream_json_schema, id="upstream_json_schema"),
        param(_try_upstream_api, id="upstream_api"),
    ],
)
