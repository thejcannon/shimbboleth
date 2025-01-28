"""
Tests using invalid pipelines for trigger steps.
"""

import pytest


@pytest.fixture
def invalid_trigger(invalid_pipeline):
    def inner(step_fields, *, path, **kwargs):
        return invalid_pipeline(
            {"steps": [{"type": "trigger", **step_fields}]},
            path=f".steps[0]{path}",
            **kwargs,
        )

    return inner


def test_missing_trigger(*, invalid_trigger):
    invalid_trigger(
        {},
        error="Expected required fields `'trigger'` to be provided for model `TriggerStep`",
        path="",
        id="missing_trigger",
    )
