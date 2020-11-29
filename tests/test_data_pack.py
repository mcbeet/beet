from pathlib import Path

from beet import BlockTag, DataPack, Function, FunctionTag, Structure


def test_equality():
    assert DataPack() == DataPack()
    assert DataPack("hello") == DataPack("hello")
    assert DataPack("hello") != DataPack("world")

    p1 = DataPack("foo", mcmeta={"pack": {"description": "bar"}})
    p2 = DataPack("foo", mcmeta={"pack": {"description": "bar"}})
    assert p1 == p2

    p1 = DataPack("foo", mcmeta={"pack": {"description": "bar", "pack_format": 6}})
    p2 = DataPack("foo", mcmeta={"pack": {"description": "bar", "pack_format": 5}})
    assert p1 != p2


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


def test_context_manager(tmp_path: Path):
    with DataPack(path=tmp_path / "foobar") as p1:
        p1["hello:world"] = Function(["say hello"], tags=["minecraft:load"])

    p2 = DataPack(path=tmp_path / "foobar")
    assert p2 != p1

    assert p2.functions["hello:world"].content == ["say hello"]
    assert p2.function_tags["minecraft:load"].content == {"values": ["hello:world"]}
    assert p2 == p1


def test_context_manager_eager(tmp_path: Path):
    with DataPack(path=tmp_path / "foobar") as p1:
        p1["hello:world"] = Function(["say hello"], tags=["minecraft:load"])

    assert DataPack(path=tmp_path / "foobar", eager=True) == p1


def test_context_manager_load_lazy(tmp_path: Path):
    with DataPack(path=tmp_path / "foobar") as p1:
        p1["hello:world"] = Function(["say hello"], tags=["minecraft:load"])

    p2 = DataPack()
    p2.load(tmp_path / "foobar", lazy=True)
    assert p2 != p1


def test_context_manager_load(tmp_path: Path):
    with DataPack(path=tmp_path / "foobar") as p1:
        p1["hello:world"] = Function(["say hello"], tags=["minecraft:load"])

    p2 = DataPack()
    p2.load(tmp_path / "foobar")
    assert p2 == p1


def test_context_manager_zipped(tmp_path: Path):
    with DataPack(path=tmp_path / "foobar.zip") as p1:
        p1["hello:world"] = Function(["say hello"], tags=["minecraft:load"])

    p2 = DataPack(path=tmp_path / "foobar.zip")

    assert p2.functions["hello:world"].content == ["say hello"]
    assert p2.function_tags["minecraft:load"].content == {"values": ["hello:world"]}
    assert p2 == p1

    p1.functions["hello:world"].content.append("say world")
    assert p2 != p1

    p2["hello"].functions["world"].content.append("say world")
    assert p2 == p1


def test_vanilla_compare(minecraft_data_pack: Path):
    assert DataPack(path=minecraft_data_pack) == DataPack(path=minecraft_data_pack)


def test_vanilla_zip(minecraft_data_pack: Path, tmp_path: Path):
    pack = DataPack(path=minecraft_data_pack)
    zipped_pack = pack.dump(tmp_path, zipped=True)
    assert DataPack(path=zipped_pack) == DataPack(path=zipped_pack)


def test_vanilla_content(minecraft_data_pack: Path):
    pack = DataPack(path=minecraft_data_pack)
    assert len(list(pack.content)) > 3000


def test_vanilla_igloo(minecraft_data_pack: Path):
    pack = DataPack(path=minecraft_data_pack)
    assert pack.structures["minecraft:igloo/top"].content["size"] == [7, 5, 8]


def test_vanilla_igloo_content(minecraft_data_pack: Path):
    pack = DataPack(path=minecraft_data_pack)
    content = dict(pack.content)
    igloo_structure = content["minecraft:igloo/top"]
    assert isinstance(igloo_structure, Structure)
    assert igloo_structure.content["size"] == [7, 5, 8]


def test_merge_tags():
    p1 = DataPack()
    p1["hello:func1"] = Function(["say foo"], tags=["minecraft:tick"])

    p2 = DataPack()
    p2["hello:func2"] = Function(["say bar"], tags=["minecraft:tick"])

    p1.merge(p2)

    assert len(p1.functions) == 2
    assert len(p1.function_tags) == 1
    assert p1.function_tags["minecraft:tick"].content == {
        "values": ["hello:func1", "hello:func2"]
    }


def test_merge_block_tags():
    p1 = DataPack()
    p1["custom:blocks"] = BlockTag({"values": ["minecraft:stone"]})

    p2 = DataPack()
    p2["custom:blocks"] = BlockTag({"values": ["minecraft:dirt"]})

    p1.merge(p2)

    assert dict(p1.block_tags) == {
        "custom:blocks": BlockTag({"values": ["minecraft:stone", "minecraft:dirt"]})
    }


def test_match():
    pack = DataPack()
    custom = pack["custom"]

    for i in range(100):
        custom[f"path/to/func_{i:02d}"] = Function([f"say {i}"])

    custom["path/to/end"] = Function(["say end"])

    custom["other/subdir/hello"] = Function(["say hello"])
    custom["other/subdir/world"] = Function(["say world"])
    custom["other/thing"] = Function(["say thing"])

    funcs = [f"path/to/func_{i:02d}" for i in range(100)]

    assert custom.functions.match() == set(funcs) | {
        "path/to/end",
        "other/subdir/hello",
        "other/subdir/world",
        "other/thing",
    }

    assert custom.functions.match("path/to/func_0*") == set(funcs[:10])
    assert custom.functions.match("path/to/func_*") == set(funcs)

    assert custom.functions.match("path/to") == set(funcs) | {"path/to/end"}
    assert custom.functions.match("path/to/func_*", "other") == set(funcs) | {
        "other/subdir/hello",
        "other/subdir/world",
        "other/thing",
    }

    assert custom.functions.match("other/subdir") == {
        "other/subdir/hello",
        "other/subdir/world",
    }


def test_proxy_match():
    pack = DataPack()
    custom = pack["custom"]
    hey = pack["hey"]

    for i in range(100):
        custom[f"path/to/func_{i:02d}"] = Function([f"say {i}"])
        hey[f"path/to/func_{i:02d}"] = Function([f"say {i}"])

    custom["path/to/end"] = Function(["say end"])

    custom["other/subdir/hello"] = Function(["say hello"])
    custom["other/subdir/world"] = Function(["say world"])
    custom["other/thing"] = Function(["say thing"])

    hey["other/subdir/hello"] = Function(["say hello"])

    custom_funcs = [f"custom:path/to/func_{i:02d}" for i in range(100)]
    hey_funcs = [f"hey:path/to/func_{i:02d}" for i in range(100)]

    assert pack.functions.match() == set(custom_funcs) | set(hey_funcs) | {
        "custom:path/to/end",
        "custom:other/subdir/hello",
        "custom:other/subdir/world",
        "custom:other/thing",
        "hey:other/subdir/hello",
    }

    assert pack.functions.match("custom:*") == set(custom_funcs) | {
        "custom:path/to/end",
        "custom:other/subdir/hello",
        "custom:other/subdir/world",
        "custom:other/thing",
    }

    assert pack.functions.match("*:other/subdir") == {
        "custom:other/subdir/hello",
        "custom:other/subdir/world",
        "hey:other/subdir/hello",
    }

    assert pack.functions.match(
        "*:path/to/func_0*", "*:path/to/end", "hey:other"
    ) == set(custom_funcs[:10]) | set(hey_funcs[:10]) | {
        "custom:path/to/end",
        "hey:other/subdir/hello",
    }
