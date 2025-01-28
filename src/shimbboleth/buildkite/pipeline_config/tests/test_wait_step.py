import pytest

from shimbboleth.buildkite.pipeline_config import WaitStep
from shimbboleth.buildkite.pipeline_config.tests.conftest import BOOLVALS


@pytest.fixture
def load_step(load_pipeline):
    def inner(step_config, **kwargs):
        return load_pipeline({"steps": [step_config]}, **kwargs).steps[0]

    return inner


def test_string__wait(*, load_pipeline):
    assert load_pipeline({"steps": ["wait"]}).steps[0] == WaitStep()


def test_string__waiter(*, load_pipeline):
    assert load_pipeline({"steps": ["waiter"]}).steps[0] == WaitStep(type="waiter")


def test_wait_null(*, load_pipeline):
    assert load_pipeline({"steps": [{"wait": None}]}).steps[0] == WaitStep()


@pytest.mark.parametrize("value, expected", BOOLVALS)
def test_continue_on_failure(value, expected, *, load_step):
    assert (
        load_step({"type": "wait", "continue_on_failure": value}).continue_on_failure
        == expected
    )
