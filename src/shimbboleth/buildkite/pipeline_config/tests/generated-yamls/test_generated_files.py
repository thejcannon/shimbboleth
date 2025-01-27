"""
Run tests against the generated files
"""

from pathlib import Path

import pytest
import yaml

GENERATED_YAMLS = list(Path(__file__).parent.rglob("**/*.yaml"))

# @TODO: Valid vs invalid


@pytest.mark.parametrize("path", GENERATED_YAMLS)
# @TODO: parameterize on `steps:` and `group:`
def test_against_generated_schema(path, *, generated_schema):
    generated_schema.validate(yaml.safe_load(path.read_text()))

@pytest.mark.parametrize("path", GENERATED_YAMLS)
def test_upstream_json_schema(path, *, upstream_schema, request):
    if request.node.get_closest_marker("upstream_schema_invalid", False):
        pytest.xfail("Upstream schema bug")

    # @UPSTREAM: No support for non-object pipelines
    upstream_schema.validate({"steps": yaml.safe_load(path.read_text())})

@pytest.mark.parametrize("path", GENERATED_YAMLS)
@pytest.mark.integration
def test_upstream_API(path, *, config, cached_bk_api):
    response = cached_bk_api.patch(
        "/organizations/thejcannon/pipelines/step-blaster",
        json={"configuration": yaml.safe_load(path.read_text())},
    )
    print(response.json())
    response.raise_for_status()
