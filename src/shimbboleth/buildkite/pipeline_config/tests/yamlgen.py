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

# @TODO: conftest.py this


# Procdure:
#   - General the YAML into a session-wide tempdir
#   - (if they don't match, copy it to repo dir, and fail)
#   - At the end, compare the files/dirs from tempdir and repo
#       (to see if there's extra files in repo not in tempdir/vice versa)
#   - (but somehow only do this if we're running a full suite?)

from pathlib import Path
from functools import wraps
import pytest
from pytest import param
import yaml
from shimbboleth.buildkite.pipeline_config import BuildkitePipeline

PIPELINES_DIR = Path(__file__).parent / "generated-yamls"


@pytest.fixture
def load_pipeline(request):
    def persistented_model_load(config, *, id=None):
        yamls_dir = PIPELINES_DIR / request.node.module.__name__
        yamls_dir.mkdir(exist_ok=True, parents=True)
        # @TODO: assert this file doesn't exist in the tempdir?

        name = request.node.name
        if id is not None:
            name += f"@{id}"

        (yamls_dir / request.node.name).with_suffix(".yaml").write_text(
            # @TODO: This should match whatever formatting we expect
            yaml.dump(config, default_flow_style=False)
        )

        return BuildkitePipeline.model_load(config)

    return persistented_model_load
