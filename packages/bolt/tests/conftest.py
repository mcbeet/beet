import pytest
from beet import run_beet


@pytest.fixture(scope="session")
def ctx():
    with run_beet({"require": ["bolt"]}) as ctx:
        yield ctx


@pytest.fixture(scope="session")
def ctx_sandbox():
    with run_beet({"require": ["bolt.contrib.sandbox"]}) as ctx:
        yield ctx
