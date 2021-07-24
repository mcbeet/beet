from pytest_insta import SnapshotFixture

from mecha import Mecha


def test_prototypes(snapshot: SnapshotFixture, mc: Mecha):
    assert snapshot("json") == list(mc.spec.prototypes)
