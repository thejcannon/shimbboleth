"""
Tests using invalid pipelines for all step types.
"""

import pytest
from shimbboleth.buildkite.pipeline_config.tests.conftest import (
    ALL_STEP_TYPE_PARAMS,
)


@pytest.fixture(params=ALL_STEP_TYPE_PARAMS)
def invalid_step(invalid_pipeline, request):
    def inner(step_fields, *, path, **kwargs):
        return invalid_pipeline(
            {"steps": [{**step_fields, **request.param.dumped_default}]},
            path=f".steps[0]{path}",
            **kwargs,
        )

    return inner


def test_invalid_key(*, invalid_step):
    invalid_step(
        {"key": "2cb75f85-79ab-43a0-b666-91dbcb64321a"},
        error="Expected `'2cb75f85-79ab-43a0-b666-91dbcb64321a'` to not be a valid UUID",
        path=".key",
        id="key_uuid",
    )


def test_depends_on__missing_step(*, invalid_step):
    invalid_step(
        {"depends_on": [{}]},
        error="Expected required fields `'step'` to be provided for model `Step.Dependency`",
        path=".depends_on[0]",
        id="depends_on_missing_step",
        upstream_schema_valid=True,
    )
