from pytest_insta import SnapshotFixture

from beet import Context

from mecha import Mecha


def test_prototypes(snapshot: SnapshotFixture, ctx: Context):
    mc = ctx.inject(Mecha)
    assert snapshot("json") == sorted(mc.spec.prototypes)
