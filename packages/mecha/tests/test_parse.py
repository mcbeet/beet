import pytest
from beet import Function
from beet.core.utils import JsonDict
from pytest_insta import SnapshotFixture

from mecha import Mecha, delegate, get_argument_examples, get_command_examples


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


def test_command_examples(snapshot: SnapshotFixture, mc: Mecha):
    assert snapshot() == mc.parse_function(get_command_examples()).dump()


@pytest.mark.parametrize(
    "argument_parser, properties, value",
    params := [
        (argument_parser, suite.get("properties", {}), value)
        for argument_parser, suites in get_argument_examples().items()
        for suite in suites
        for value in suite["examples"]
    ],
    ids=[f"{argument_parser}_{i}" for i, (argument_parser, _, _) in enumerate(params)],
)
def test_argument_examples(
    snapshot: SnapshotFixture,
    mc: Mecha,
    argument_parser: str,
    properties: JsonDict,
    value: str,
):
    if argument_parser not in mc.spec.parsers:
        pytest.skip()

    stream = mc.create_token_stream(value)

    with stream.syntax(literal=r"\S+"), stream.provide(properties=properties):
        assert snapshot() == "\n---\n".join(
            [
                argument_parser,
                str(properties),
                value,
                delegate(stream, argument_parser).dump(),
            ]
        )
