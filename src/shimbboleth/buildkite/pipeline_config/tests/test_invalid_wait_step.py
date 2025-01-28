"""
Tests using invalid pipelines for wait steps.
"""

import pytest
from pytest import param


@pytest.fixture
def invalid_wait(invalid_pipeline):
    def inner(step_fields, *, path, **kwargs):
        return invalid_pipeline(
            {"steps": [{"type": "wait", **step_fields}]},
            path=f".steps[0]{path}",
            **kwargs,
        )

    return inner
