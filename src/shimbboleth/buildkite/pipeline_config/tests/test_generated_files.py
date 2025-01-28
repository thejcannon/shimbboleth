"""
Run tests against the generated files
"""

from pathlib import Path

import pytest
import yaml
from shimbboleth.buildkite.pipeline_config.tests.yamlgen import PIPELINES_DIR

GENERATED_YAMLS = [

]

@pytest.fixture(
    params=(
        pytest.param(path, id=str(path.relative_to(PIPELINES_DIR)))
        for path in PIPELINES_DIR.rglob("**/*.yaml")
    )
)
def pipeline_config(request):
    docs = list(yaml.safe_load_all(request.param.read_text()))
    if docs[0].get("upstream_schema_invalid", False):
        request.node.add_marker("upstream_schema_invalid")
    # @TODO: Valid vs invalid

    return docs[-1]




# @TODO: parameterize on `steps:` and `group:`
def test_against_generated_schema(pipeline_config, *, generated_schema):
    generated_schema.validate(pipeline_config)


# @UPSTREAM: No support for non-object pipelines
def test_upstream_json_schema(pipeline_config, *, upstream_schema, request):
    if request.node.get_closest_marker("upstream_schema_invalid") is not None:
        request.node.add_marker(pytest.mark.xfail(reason="Upstream schema bug", strict=True))

    upstream_schema.validate(pipeline_config)


@pytest.mark.integration
def test_upstream_API(pipeline_config, *, config, cached_bk_api):
    response = cached_bk_api.patch(
        "/organizations/thejcannon/pipelines/step-blaster",
        json={"configuration": pipeline_config},
    )
    print(response.json())
    response.raise_for_status()
