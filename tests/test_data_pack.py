from beet import DataPack, Function, FunctionTag, Structure


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

    p2.functions["hello:world"].content.append("say world")

    assert p1.functions["hello:world"] != p2.functions["hello:world"]
    assert p1["hello"] != p2["hello"]
    assert p1 != p2

    p1["hello"].functions["world"].content.append("say world")

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
    with DataPack(path=tmpdir / "foobar") as p1:
        p1["hello:world"] = Function(["say hello"], tags=["minecraft:load"])

    p2 = DataPack(path=tmpdir / "foobar")
    assert p2 != p1

    assert p2.functions["hello:world"].content == ["say hello"]
    assert p2.function_tags["minecraft:load"].content == {"values": ["hello:world"]}
    assert p2 == p1


def test_context_manager_eager(tmpdir):
    with DataPack(path=tmpdir / "foobar") as p1:
        p1["hello:world"] = Function(["say hello"], tags=["minecraft:load"])

    assert DataPack(path=tmpdir / "foobar", eager=True) == p1


def test_context_manager_load(tmpdir):
    with DataPack(path=tmpdir / "foobar") as p1:
        p1["hello:world"] = Function(["say hello"], tags=["minecraft:load"])

    p2 = DataPack()
    p2.load(tmpdir / "foobar")
    assert p2 != p1


def test_context_manager_load_eager(tmpdir):
    with DataPack(path=tmpdir / "foobar") as p1:
        p1["hello:world"] = Function(["say hello"], tags=["minecraft:load"])

    p2 = DataPack()
    p2.load(tmpdir / "foobar", eager=True)
    assert p2 == p1


def test_context_manager_zipped(tmpdir):
    with DataPack(path=tmpdir / "foobar.zip") as p1:
        p1["hello:world"] = Function(["say hello"], tags=["minecraft:load"])

    p2 = DataPack(path=tmpdir / "foobar.zip")

    assert p2.functions["hello:world"].content == ["say hello"]
    assert p2.function_tags["minecraft:load"].content == {"values": ["hello:world"]}
    assert p2 == p1

    p1.functions["hello:world"].content.append("say world")
    assert p2 != p1

    p2["hello"].functions["world"].content.append("say world")
    assert p2 == p1


def test_compare_vanilla(minecraft_data_pack):
    assert DataPack(path=minecraft_data_pack) == DataPack(path=minecraft_data_pack)


def test_zip_vanilla(minecraft_data_pack, tmp_path):
    pack = DataPack(path=minecraft_data_pack)
    zipped_pack = pack.dump(tmp_path, zipped=True)
    assert DataPack(path=zipped_pack) == DataPack(path=zipped_pack)


def test_all_files(minecraft_data_pack):
    pack = DataPack(path=minecraft_data_pack)
    assert len(list(pack.all_files())) > 3000


def test_igloo(minecraft_data_pack):
    pack = DataPack(path=minecraft_data_pack)
    assert pack.structures["minecraft:igloo/top"].content["size"] == [7, 5, 8]


def test_igloo_all_files(minecraft_data_pack):
    pack = DataPack(path=minecraft_data_pack)
    all_files = dict(pack.all_files())
    igloo_structure = all_files["minecraft:igloo/top"]
    assert isinstance(igloo_structure, Structure)
    assert igloo_structure.content["size"] == [7, 5, 8]
