import pytest
from pytest import param

from shimbboleth.buildkite.pipeline_config import BuildkitePipeline
from shimbboleth.buildkite.pipeline_config.tests.conftest import ALL_SUBSTEP_TYPE_PARAMS


@pytest.fixture(params=ALL_SUBSTEP_TYPE_PARAMS)
def load_step(load_pipeline, request):
    def inner(step_fields, *, id=None):
        return load_pipeline(
            [{**step_fields, **request.param.dumped_default}], id=id
        ).steps[0]

    inner.steptype = request.param
    return inner


def test_branches(*, load_step):
    assert load_step({"branches": "master"}, id="string").branches == ["master"]
    assert load_step({"branches": ["master"]}, id="list").branches == ["master"]


def test_type_label_name(*, load_step):
    steptype = load_step.steptype
    assert load_step({"type": steptype.type}, id="type").type == steptype.type
    assert load_step({"type": steptype.type, "label": "label"}, id="type-label").label == "label"
    assert load_step({"type": steptype.type, "name": "name"}, id="type-name").label == "name"
    step = load_step({"type": steptype.type, "label": "label", "name": "name"}, id="type-label-name")
    assert step.label == "name"


@pytest.mark.parametrize("step_param", [
    param for param in ALL_SUBSTEP_TYPE_PARAMS
    if param.id not in ("command", "trigger")
])
def test_stepname_label_name(step_param, *, load_pipeline):
    def load_step(step_fields, *, id=None):
        return load_pipeline(
            [{**step_fields, **step_param.dumped_default}], id=id
        ).steps[0]

    stepname_base = {step_param.stepname: step_param.stepname}
    assert load_step(stepname_base, id="stepname").label == step_param.stepname
    assert load_step({**stepname_base, "label": "label"}, id="stepname-label").label == "label"
    assert load_step({**stepname_base, "name": "name"}, id="stepname-name").label == "name"
    step = load_step({**stepname_base, "label": "label", "name": "name"}, id="stepname-label-name")
    assert step.label == "name"
