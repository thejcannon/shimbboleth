"""
Tests using valid pipelines for all substep types (all step types except group steps).
"""

import pytest

from shimbboleth.buildkite.pipeline_config.tests.conftest import ALL_SUBSTEP_TYPE_PARAMS


@pytest.fixture(params=ALL_SUBSTEP_TYPE_PARAMS)
def load_step(load_pipeline, request):
    def inner(step_fields, **kwargs):
        return load_pipeline(
            {"steps": [{**step_fields, **request.param.dumped_default}]}, **kwargs
        ).steps[0]

    inner.steptype = request.param
    return inner


def test_branches(*, load_step):
    assert (
        load_step({"branches": "master"}, id="string").branches
        == load_step({"branches": ["master"]}, id="list").branches
        == ["master"]
    )


def test_label_name(*, load_step):
    steptype = load_step.steptype
    assert load_step({"label": "label"}, id="type-label").label == "label"
    assert (
        load_step({"name": "name"}, id="type-name").label
        == load_step({"label": "label", "name": "name"}, id="type-label-name").label
        == "name"
    )
    stepname = steptype.stepname
    if stepname in ("command", "trigger"):
        return

    assert load_step({stepname: stepname}, id="stepname").label == stepname
    assert (
        load_step({stepname: stepname, "label": "label"}, id="stepname-label").label
        == "label"
    )
    assert (
        load_step({stepname: stepname, "name": "name"}, id="stepname-name").label
        == load_step(
            {stepname: stepname, "label": "label", "name": "name"},
            id="stepname-label-name",
        ).label
        == "name"
    )


@pytest.mark.parametrize("step_param", ALL_SUBSTEP_TYPE_PARAMS)
def test_nested_substep(step_param, *, load_pipeline):
    def load_step(step_fields, **kwargs):
        return load_pipeline({"steps": [step_fields]}, **kwargs).steps[0]

    # @TODO: When using nested format, type is implied by the step name
    #   (so it is rejected in the upstream API)
    defaults_without_type = {
        k: v for k, v in step_param.ctor_defaults.items() if k != "type"
    }
    nested_step = {step_param.stepname: defaults_without_type}
    step = load_step(nested_step, id="nested")
    assert step == step_param.ctor()
