import pytest

from mecha import Mecha


@pytest.fixture(scope="session")
def mc():
    return Mecha()
