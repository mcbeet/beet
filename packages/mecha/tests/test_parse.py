from importlib.resources import read_text

from beet import Function
from pytest_insta import SnapshotFixture

from mecha import Mecha


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
    function = read_text("mecha.resources", "wiki_examples.mcfunction")
    assert snapshot() == mc.parse_function(function).dump()
