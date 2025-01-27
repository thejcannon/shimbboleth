import pytest

from shimbboleth.buildkite.pipeline_config import BuildkitePipeline, BlockStep


@pytest.fixture
def load_step(load_pipeline):
    def inner(step_config, *, id=None):
        return load_pipeline([step_config], id=id).steps[0]

    return inner


@pytest.mark.upstream_schema_invalid
def test_string__manual(*, load_pipeline):
    assert load_pipeline({"steps": ["manual"]}).steps[0] == BlockStep(type="manual")


def test_string__block(*, load_pipeline):
    assert load_pipeline({"steps": ["block"]}).steps[0] == BlockStep()


@pytest.mark.parametrize("value", ["passed", "failed", "running"])
def test_blocked_state(value, *, load_step):
    assert load_step({"blocked_state": value}).blocked_state == value
