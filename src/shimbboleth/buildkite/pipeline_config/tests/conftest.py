import pytest

# Register modules for assertion rewriting
pytest.register_assert_rewrite("shimbboleth.buildkite.pipeline_config.tests.bases")
pytest.register_assert_rewrite("shimbboleth.buildkite.pipeline_config.tests.helpers")

from shimbboleth.buildkite.pipeline_config.tests.helpers._known_xfails import mark_known_xfails # noqa: E402
from shimbboleth.buildkite.pipeline_config.tests.helpers._filter_empty_paramsets import filter_empty_paramsets # noqa: E402


PYTEST_CONFIG: pytest.Config | None = None


@pytest.fixture(scope="session", autouse=True)
def _store_config(pytestconfig: pytest.Config) -> None:
    global PYTEST_CONFIG
    PYTEST_CONFIG = pytestconfig



def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    mark_known_xfails(items)
    filter_empty_paramsets(items)

