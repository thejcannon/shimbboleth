import pytest

from shimbboleth.buildkite.pipeline_config import BuildkitePipeline, CommandStep


@pytest.fixture
def load_step(load_pipeline):
    def inner(step_config, *, id=None):
        return load_pipeline([{**step_config, "type": "command"}], id=id).steps[0]

    return inner


def test_string__command(*, load_pipeline):
    assert load_pipeline({"steps": ["command"]}).steps[0] == CommandStep()


def test_string__commands(*, load_pipeline):
    assert load_pipeline({"steps": ["commands"]}).steps[0] == CommandStep(
        type="commands"
    )


def test_string__script(*, load_pipeline):
    assert load_pipeline({"steps": ["script"]}).steps[0] == CommandStep(type="script")
