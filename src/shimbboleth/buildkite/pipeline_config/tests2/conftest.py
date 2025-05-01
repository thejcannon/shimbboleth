import pytest


PYTEST_CONFIG: pytest.Config | None = None


@pytest.fixture(scope="session", autouse=True)
def _store_config(pytestconfig: pytest.Config) -> None:
    global PYTEST_CONFIG
    PYTEST_CONFIG = pytestconfig
