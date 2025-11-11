import pytest

from mecha import CommandSpec, CommandTree, Mecha, get_parsers


@pytest.fixture(scope="session")
def mc():
    return Mecha()


@pytest.fixture
def mc_1_17(mc: Mecha):
    previous_spec = mc.spec
    mc.spec = CommandSpec(
        tree=CommandTree.load_from(version="1.17"),
        parsers=get_parsers("1.17"),
    )

    yield mc

    mc.spec = previous_spec
