import pytest
from beet import Context, DataPack, run_beet
from pytest_insta import SnapshotFixture

from mecha import Mecha
from mecha.contrib.statistics import Analyzer, Summary


@pytest.fixture(scope="session")
def ctx_stats():
    with run_beet({"require": ["mecha.contrib.statistics"]}) as ctx:
        yield ctx


def test_smithed_core(snapshot: SnapshotFixture, ctx_stats: Context):
    mc = ctx_stats.inject(Mecha)
    analyzer = ctx_stats.inject(Analyzer)
    mc.compile(DataPack(path="tests/resources/SmithedCore-DP-0.0.1.zip"))
    assert snapshot() == str(Summary(mc.spec, analyzer.stats))
