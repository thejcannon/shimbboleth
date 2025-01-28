"""
@TODO: ...
"""

import pytest
from shimbboleth.buildkite.pipeline_config.step import Step
from shimbboleth.buildkite.pipeline_config.tests.conftest import (
    ALL_STEP_TYPE_PARAMS,
    BOOLVALS,
)


@pytest.fixture(params=ALL_STEP_TYPE_PARAMS)
def load_step(load_pipeline, request):
    def inner(step_fields, **kwargs):
        return load_pipeline(
            {"steps": [{**step_fields, **request.param.dumped_default}]}, **kwargs
        ).steps[0]

    return inner


@pytest.mark.parametrize("value, expected", BOOLVALS)
def test_allow_dependency_failure(value, expected, *, load_step):
    assert (
        load_step({"allow_dependency_failure": value}).allow_dependency_failure
        == expected
    )


def test_if(*, load_step):
    assert load_step({"if": "build.number == 1"}).if_condition == "build.number == 1"


def test_depends_on(*, load_step):
    assert (
        load_step({"depends_on": "other"}, id="str").depends_on
        == load_step({"depends_on": ["other"]}, id="list[str]").depends_on
        == (load_step({"depends_on": [{"step": "other"}]}, id="list[dict]").depends_on)
        == [Step.Dependency(step="other")]
    )


@pytest.mark.parametrize("value, expected", BOOLVALS)
def test_depends_on__allow_failure(value, expected, *, load_step):
    assert (
        load_step(
            {"depends_on": [{"step": "other", "allow_failure": value}]}, id="scalar"
        )
        .depends_on[0]
        .allow_failure
    ) == expected


def test_key__with_aliases(*, load_step):
    assert (
        load_step({"key": "key"}, id="key").key
        == load_step({"key": "key", "id": "id"}, id="key-id").key
        == load_step(
            {"key": "key", "id": "id", "identifier": "identifier"},
            id="key-id-identifier",
        ).key
        == "key"
    )
    assert (
        load_step({"identifier": "identifier"}, id="identifier").key
        == load_step(
            {"id": "id", "identifier": "identifier"},
            id="id-identifier",
        ).key
        == "identifier"
    )
    assert load_step({"id": "id"}, id="id").key == "id"


# @TEST An integration test that the above aliases are legit
