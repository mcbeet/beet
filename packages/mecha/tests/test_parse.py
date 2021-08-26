import pytest
from beet import Function
from pytest_insta import SnapshotFixture

from mecha import Mecha, delegate, get_wiki_argument_types, get_wiki_examples


def test_basic1(snapshot: SnapshotFixture, mc: Mecha):
    assert snapshot() == mc.parse_command("gamerule fallDamage false").dump()


def test_basic2(snapshot: SnapshotFixture, mc: Mecha):
    function = Function(
        [
            "gamerule doMobLoot false",
            "gamerule doDaylightCycle false",
        ]
    )
    assert snapshot() == mc.parse_function(function).dump()


def test_wiki_examples(snapshot: SnapshotFixture, mc: Mecha):
    assert snapshot() == mc.parse_function(get_wiki_examples()).dump()


@pytest.mark.parametrize(
    "argument_type, value",
    [
        (argument_type, value)
        for argument_type, examples in get_wiki_argument_types().items()
        for value in examples
    ],
)
def test_wiki_argument_types(
    snapshot: SnapshotFixture,
    mc: Mecha,
    argument_type: str,
    value: str,
):
    if argument_type not in mc.spec.parsers:
        pytest.skip()

    stream = mc.create_token_stream(value)

    with stream.syntax(literal=r"\S+"):
        assert snapshot() == delegate(stream, argument_type).dump()
