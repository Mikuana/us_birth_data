import tempfile
from pathlib import Path

import pytest


@pytest.fixture()
def tmpdir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


# noinspection SpellCheckingInspection
def pytest_addoption(parser):
    parser.addoption(
        "--skip-slow", action="store_true", default=False, help="skip slow tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")


# noinspection SpellCheckingInspection
def pytest_collection_modifyitems(config, items):
    """ --skip-slow given in cli: do not skip slow tests """
    if config.getoption("--skip-slow"):
        skip_slow = pytest.mark.skip(reason="need --run-slow option to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)
    else:
        return
