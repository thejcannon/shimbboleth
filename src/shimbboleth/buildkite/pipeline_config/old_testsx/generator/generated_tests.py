"""
This module contains the functions that'll get executed as "generated tests".

This is referenced in `conftest.py` where, for each test that loads a pipeline,
we generate a new test item for each of the test functions here.

NOTE: The tests here are repeated/enumerated in `conftest.py`
"""

import contextlib

import pytest
from jsonschema import ValidationError


def test_generated_schema(json_data, *, request, generated_schema):
    context = (
        pytest.raises(ValidationError)
        if request.node.get_closest_marker("generated_schema_invalid")
        else contextlib.nullcontext()
    )
    with context:
        generated_schema.validate(json_data)


def test_upstream_json_schema(pipeline_config, *, upstream_schema, request):
    context = (
        pytest.raises(ValidationError)
        if request.node.get_closest_marker("upstream_schema_invalid")
        else contextlib.nullcontext()
    )
    with context:
        upstream_schema.validate(pipeline_config)


# @TODO: We can run the test if we have the cached value. Do we want to?
@pytest.mark.integration
def test_upstream_API(pipeline_config, *, config, cached_bk_api):
    response = cached_bk_api.patch(
        "/organizations/thejcannon/pipelines/step-blaster",
        json={"configuration": pipeline_config},
    )
    print(response.json())
    response.raise_for_status()
