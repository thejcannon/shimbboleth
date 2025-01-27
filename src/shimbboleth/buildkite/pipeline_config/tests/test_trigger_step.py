import pytest

from shimbboleth.buildkite.pipeline_config import BuildkitePipeline, TriggerStep
from shimbboleth.buildkite.pipeline_config.tests.conftest import BOOLVALS, SKIP_VALS


@pytest.fixture
def load_step(load_pipeline):
    def inner(step_config, *, id=None):
        return load_pipeline([{"trigger": "trigger", **step_config}], id=id).steps[0]

    return inner


@pytest.mark.parametrize("value, expected", BOOLVALS.items())
def test_async(value, expected, *, load_step):
    assert load_step({"async": value}).is_async == expected


def test_build(*, load_step):
    assert (
        load_step({"build": {"branch": "branch"}}, id="branch").build.branch == "branch"
    )
    assert (
        load_step({"build": {"commit": "commit"}}, id="commit").build.commit == "commit"
    )
    assert (
        load_step({"build": {"message": "message"}}, id="message").build.message
        == "message"
    )
    # @TEST: env types
    assert load_step(
        {"build": {"env": {"str": "string", "int": 0, "bool": True}}},
        id="env",
    ).build.env == {"str": "string", "int": 0, "bool": True}
    assert load_step(
        {"build": {"meta_data": {"str": "string", "int": 0, "bool": True}}},
        id="meta_data",
    ).build.meta_data == {"str": "string", "int": 0, "bool": True}


@pytest.mark.parametrize("value, expected", SKIP_VALS.items())
def test_skip(value, expected, *, load_step):
    assert load_step({"skip": value}).skip == expected


@pytest.mark.parametrize("value, expected", BOOLVALS.items())
def test_soft_fail(value, expected, *, load_step):
    assert load_step({"soft_fail": value}).soft_fail == expected
