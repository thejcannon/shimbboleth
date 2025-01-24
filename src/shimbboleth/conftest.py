"""
Pytest config for all of shimbboleth testing.

Currently configures:
    - Integration test support
    - Setting `SHIMBBOLETH_PYTESTING` so we can opt-out of
        certain behaviors when not testing shimbboleth
"""

import pytest
import os


def pytest_addoption(parser):
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="Run integration tests",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: mark test as integration (run with `--integration`)"
    )
    config.addinivalue_line("markers", "meta(**kwargs): Attach metadata to a test")


def pytest_runtest_setup(item):
    if not item.config.getoption("--integration") and item.get_closest_marker(
        "integration"
    ):
        pytest.skip("Integration test; use `-m integration` to run")

    os.environ["SHIMBBOLETH_PYTESTING"] = "1"
