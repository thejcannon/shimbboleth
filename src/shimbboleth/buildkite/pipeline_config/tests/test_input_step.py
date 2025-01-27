import pytest

from shimbboleth.buildkite.pipeline_config import BuildkitePipeline, InputStep


@pytest.fixture
def load_step(load_pipeline):
    def inner(step_config, *, id=None):
        return load_pipeline([step_config], id=id).steps[0]

    return inner


def test_string__input(*, load_pipeline):
    assert load_pipeline({"steps": ["input"]}).steps[0] == InputStep()
