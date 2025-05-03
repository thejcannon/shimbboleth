import pytest

from shimbboleth.buildkite.pipeline_config import BlockStep


@pytest.fixture
def load_step(load_pipeline):
    def inner(step_config, **kwargs):
        return load_pipeline(
            {"steps": [{**step_config, "type": "block"}]}, **kwargs
        ).steps[0]

    return inner


@pytest.mark.upstream_schema_invalid
def test_string__manual(*, load_pipeline):
    assert load_pipeline({"steps": ["manual"]}).steps[0] == BlockStep(type="manual")


def test_string__block(*, load_pipeline, request):
    assert load_pipeline({"steps": ["block"]}).steps[0] == BlockStep()


@pytest.mark.parametrize("value", ["passed", "failed", "running"])
def test_blocked_state(value, *, load_step):
    assert load_step({"blocked_state": value}).blocked_state == value
