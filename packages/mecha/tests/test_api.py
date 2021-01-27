from beet import DataPack

from mecha import Mecha


def test_init_data_pack():
    pack = DataPack("demo")
    mc = Mecha(pack)

    assert mc.default_namespace == "demo"
    assert mc.default_path == ""
    assert mc.data_pack is pack


def test_init_data_pack_with_args():
    pack = DataPack("demo")
    mc = Mecha(pack, default_namespace="hello", default_path="world")

    assert mc.default_namespace == "hello"
    assert mc.default_path == "world"
    assert mc.data_pack is pack


def test_resolve_path():
    mc = Mecha(DataPack("demo"))

    assert mc.resolve_path("foo") == "demo:foo"
    assert mc.resolve_path("foo/bar") == "demo:foo/bar"
    assert mc.resolve_path(":foo") == "demo:foo"
    assert mc.resolve_path(":foo/bar") == "demo:foo/bar"
    assert mc.resolve_path("thing:foo") == "thing:foo"
    assert mc.resolve_path("thing:foo/bar") == "thing:foo/bar"


def test_resolve_path_with_root():
    mc = Mecha(DataPack("demo"), default_path="root")

    assert mc.resolve_path("foo") == "demo:root/foo"
    assert mc.resolve_path("foo/bar") == "demo:root/foo/bar"
    assert mc.resolve_path(":foo") == "demo:foo"
    assert mc.resolve_path(":foo/bar") == "demo:foo/bar"
    assert mc.resolve_path("thing:foo") == "thing:foo"
    assert mc.resolve_path("thing:foo/bar") == "thing:foo/bar"
