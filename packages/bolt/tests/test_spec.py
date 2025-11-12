from beet import Context
from mecha import Mecha
from pytest_insta import SnapshotFixture


def test_prototypes(snapshot: SnapshotFixture, ctx: Context):
    mc = ctx.inject(Mecha)
    assert snapshot("json") == list(sorted(mc.spec.prototypes))
