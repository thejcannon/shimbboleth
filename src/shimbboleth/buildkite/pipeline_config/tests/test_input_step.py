import pytest

from shimbboleth.buildkite.pipeline_config import BuildkitePipeline, InputStep


@pytest.fixture
def load_step(load_pipeline):
    def inner(step_config, **kwargs):
        return load_pipeline({"steps": [step_config]}, **kwargs).steps[0]

    return inner


def test_string__input(*, load_pipeline):
    assert load_pipeline({"steps": ["input"]}).steps[0] == InputStep()
