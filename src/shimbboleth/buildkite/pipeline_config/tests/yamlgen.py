"""
This module is responsible for generating the pipelines in the `pipelienes` directory.

We use a multi-step process for a few reasons:
    - YAML files on disk are easier to grok than Python
        - And closer align with Buildkite's usage
    - It's easier to lint YAML files than Python code
        - Ensure we aren't duplicating test cases, etc...
    - It's easier to review changes to YAML files than Python code
    - We can define a single test case, and it be "expanded" into multiple
        tests scenarios

However it does lead to some complications:
    - We need to ensure we fail (especially in CI) if we don't have the right files generated
"""

# @TODO: Instead, what if we ran each test in test collection,
#   ensuring the load_pipeline fixture returned some "MockAny" object
#   then we can generate more test cases?


# Procedure:
#   - General the YAML into a session-wide tempdir
#   - (if they don't match, copy it to repo dir, and fail)
#   - At the end, compare the files/dirs from tempdir and repo
#       (to see if there's extra files in repo not in tempdir/vice versa)
#   - (but somehow only do this if we're running a full suite?)

from pathlib import Path
import pytest
from shimbboleth.buildkite.pipeline_config import BuildkitePipeline
from shimbboleth.internal.clay.validation import ValidationError

PIPELINES_DIR = Path(__file__).parent / "generated-yamls"


@pytest.fixture
def load_pipeline(request):
    def persistented_model_load(config, *, id=None, upstream_schema_invalid=False):
        assert isinstance(config, dict)

        docs = [config]
        name = request.node.nodeid.split("::", 1)[-1]
        if id is not None:
            name += f"@{id}"

        front_matter = {}
        if upstream_schema_invalid or request.node.get_closest_marker(
            "upstream_schema_invalid"
        ):
            front_matter["upstream_schema_invalid"] = True

        if front_matter:
            docs.insert(0, front_matter)

        return BuildkitePipeline.model_load(config)

    return persistented_model_load


@pytest.fixture
def invalid_pipeline(request, load_pipeline):
    def persistented_model_load(
        config, *, error, path, id=None, upstream_schema_valid=False
    ):
        with pytest.raises(ValidationError) as e:
            load_pipeline(
                config, id=id, upstream_schema_invalid=not upstream_schema_valid
            )
        assert error in str(e.value)
        assert f"Path: {path}\n" in str(e.value) + "\n"

    return persistented_model_load
