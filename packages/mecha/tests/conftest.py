import pytest

from mecha import Mecha


@pytest.fixture(scope="session")
def mc():
    return Mecha()


@pytest.fixture
def mc_multiline(mc: Mecha):
    previous_multiline = mc.spec.multiline
    mc.spec.multiline = True
    yield mc
    mc.spec.multiline = previous_multiline
