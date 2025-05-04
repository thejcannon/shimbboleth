import pathlib

import pytest
import re

# Register modules for assertion rewriting
pytest.register_assert_rewrite("shimbboleth.buildkite.pipeline_config.tests.bases")
pytest.register_assert_rewrite("shimbboleth.buildkite.pipeline_config.tests.helpers")


PYTEST_CONFIG: pytest.Config | None = None


@pytest.fixture(scope="session", autouse=True)
def _store_config(pytestconfig: pytest.Config) -> None:
    global PYTEST_CONFIG
    PYTEST_CONFIG = pytestconfig


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Mark tests from xfail file as expected to fail."""
    xfail_file = pathlib.Path(__file__).parent / "xfail_nodeids.txt"

    if not xfail_file.exists():
        return

    nodeid_patterns = {
        re.compile(re.escape(line.strip()).replace("\\*", "\w+"))
        for line in xfail_file.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    }

    for item in items:
        for pattern in nodeid_patterns:
            if pattern.match(item.nodeid):
                item.add_marker(pytest.mark.xfail(reason="Listed in xfail_nodeids.txt", strict=True))
