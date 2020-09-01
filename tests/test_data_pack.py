from beet import DataPack, Function, FunctionTag


def test_equality():
    assert DataPack() == DataPack()
    assert DataPack("hello") == DataPack("hello")
    assert DataPack("hello") != DataPack("world")
    assert DataPack("foo", "bar", 2) != DataPack("foo", "bar", 3)
    assert DataPack("foo", "bar") != DataPack("foo", "baz")


def test_namespaces():
    p1 = DataPack()
    p2 = DataPack()

    assert p1 == p2
    assert p1["hello"] == p2["hello"]

    del p1["hello"]

    assert p1 != p2
    assert p1.keys() != p2.keys()

    p1["hello:world"] = Function(["say hello"])

    assert p1 != p2
    assert p1.keys() == p2.keys()
    assert p1["hello"] != p2["hello"]

    p2["hello:world"] = Function(["say hello"])

    assert p1 == p2
    assert p1["hello"] == p2["hello"]

    p2.functions["hello:world"].lines.append("say world")

    assert p1.functions["hello:world"] != p2.functions["hello:world"]
    assert p1["hello"] != p2["hello"]
    assert p1 != p2

    p1["hello"].functions["world"].lines.append("say world")

    assert p1.functions["hello:world"] == p2.functions["hello:world"]
    assert p1["hello"] == p2["hello"]
    assert p1 == p2


def test_with_tags():
    p1 = DataPack()
    p2 = DataPack()

    p1["hello:world"] = Function(["say hello"], tags=["minecraft:load"])

    assert p1 != p2

    p2["hello"]["world"] = Function(["say hello"])
    p2["minecraft"].function_tags["load"] = FunctionTag({"values": ["hello:world"]})

    assert p1 == p2


def test_context_manager(tmpdir):
    with DataPack(path=tmpdir / "foobar") as data:
        data["hello:world"] = Function("say hello\n", tags=["minecraft:load"])

    assert DataPack(path=tmpdir / "foobar") == data


def test_context_manager_zipped(tmpdir):
    with DataPack(path=tmpdir / "foobar.zip") as data:
        data["hello:world"] = Function("say hello\n", tags=["minecraft:load"])

    other = DataPack(path=tmpdir / "foobar.zip")
    assert other == data

    data.functions["hello:world"].lines.append("say world")
    assert other != data

    other["hello"].functions["world"].lines.append("say world")
    assert other == data


def test_zip_vanilla(minecraft_data_pack, tmp_path):
    pack = DataPack(path=minecraft_data_pack)
    zipped_pack = pack.dump(tmp_path, zipped=True)
    assert DataPack(path=zipped_pack) == pack
