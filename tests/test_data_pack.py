from dataclasses import dataclass
from pathlib import Path
from typing import Any

from beet import (
    BlockTag,
    DataPack,
    Drop,
    Function,
    FunctionTag,
    JsonFile,
    JsonFileBase,
    LootTable,
    Mcmeta,
    MergePolicy,
    Structure,
    select_files,
)


def test_equality():
    assert DataPack() == DataPack()
    assert DataPack("hello") == DataPack("hello")
    assert DataPack("hello") != DataPack("world")

    p1 = DataPack("foo", mcmeta=Mcmeta({"pack": {"description": "bar"}}))
    p2 = DataPack("foo", mcmeta=Mcmeta({"pack": {"description": "bar"}}))
    assert p1 == p2

    p1 = DataPack(
        "foo", mcmeta=Mcmeta({"pack": {"description": "bar", "pack_format": 6}})
    )
    p2 = DataPack(
        "foo", mcmeta=Mcmeta({"pack": {"description": "bar", "pack_format": 5}})
    )
    assert p1 != p2


def test_namespaces():
    p1 = DataPack()
    p2 = DataPack()

    assert p1 == p2
    assert p1["hello"] == p2["hello"]

    del p1["hello"]

    assert dict(p1) != dict(p2)
    assert p1.keys() != p2.keys()
    assert p1 == p2

    del p1["hello"]

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

    p1["hello"].functions["world"].lines.append("say world")  # type: ignore

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


def test_tag_replace():
    p1 = DataPack()
    p1["demo:foo"] = Function(["say hello"], tags=["minecraft:load"])

    p2 = DataPack()
    p2["minecraft:load"] = FunctionTag({"values": ["demo:bar"], "replace": True})

    p1.merge(p2)

    assert p1 == {
        "demo": {Function: {"foo": Function(["say hello"])}},
        "minecraft": {
            FunctionTag: {
                "load": FunctionTag({"values": ["demo:bar"], "replace": True})
            }
        },
    }


def test_context_manager(tmp_path: Path):
    with DataPack(path=tmp_path / "foobar") as p1:
        p1["hello:world"] = Function(["say hello"], tags=["minecraft:load"])

    p2 = DataPack(path=tmp_path / "foobar")
    assert p2 == p1

    assert p2.functions["hello:world"].lines == ["say hello"]
    assert p2.function_tags["minecraft:load"].data == {"values": ["hello:world"]}
    assert p2 == p1


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

    assert p2.functions["hello:world"].lines == ["say hello"]
    assert p2.function_tags["minecraft:load"].data == {"values": ["hello:world"]}
    assert p2 == p1

    p1.functions["hello:world"].lines.append("say world")
    assert p2 != p1

    p2["hello"].functions["world"].lines.append("say world")
    assert p2 == p1


def test_vanilla_compare(minecraft_data_pack: Path):
    assert DataPack(path=minecraft_data_pack) == DataPack(path=minecraft_data_pack)


def test_vanilla_zip(minecraft_data_pack: Path, tmp_path: Path):
    pack = DataPack(path=minecraft_data_pack)
    zipped_pack = pack.save(tmp_path, zipped=True)
    assert DataPack(path=zipped_pack) == DataPack(path=zipped_pack)


def test_vanilla_content(minecraft_data_pack: Path):
    pack = DataPack(path=minecraft_data_pack)
    assert len(list(pack.content)) > 3000


def test_vanilla_igloo(minecraft_data_pack: Path):
    pack = DataPack(path=minecraft_data_pack)
    assert pack.structures["minecraft:igloo/top"].data["size"] == [7, 5, 8]


def test_vanilla_igloo_content(minecraft_data_pack: Path):
    pack = DataPack(path=minecraft_data_pack)
    content = dict(pack.content)
    igloo_structure = content["minecraft:igloo/top"]
    assert isinstance(igloo_structure, Structure)
    assert igloo_structure.data["size"] == [7, 5, 8]


def test_append_functions():
    func1 = Function(["say foo"])
    func2 = Function(["say bar"])
    func1.append(func2)

    assert func1 == Function(["say foo", "say bar"])


def test_prepend_functions():
    func1 = Function(["say foo"])
    func2 = Function(["say bar"])
    func1.prepend(func2)

    assert func1 == Function(["say bar", "say foo"])


def test_merge_tags():
    p1 = DataPack()
    p1["hello:func1"] = Function(["say foo"], tags=["minecraft:tick"])

    p2 = DataPack()
    p2["hello:func2"] = Function(["say bar"], tags=["minecraft:tick"])

    p1.merge(p2)

    assert len(p1.functions) == 2
    assert len(p1.function_tags) == 1
    assert p1.function_tags["minecraft:tick"].data == {
        "values": ["hello:func1", "hello:func2"]
    }


def test_prepend_tags():
    tag1 = FunctionTag({"values": ["hello:func1"]})
    tag2 = FunctionTag({"values": ["hello:func2"]})
    tag1.prepend(tag2)

    assert tag1.data == {"values": ["hello:func2", "hello:func1"]}


def test_merge_block_tags():
    p1 = DataPack()
    p1["custom:blocks"] = BlockTag({"values": ["minecraft:stone"]})

    p2 = DataPack()
    p2["custom:blocks"] = BlockTag({"values": ["minecraft:dirt"]})

    p1.merge(p2)

    assert dict(p1.block_tags) == {
        "custom:blocks": BlockTag({"values": ["minecraft:stone", "minecraft:dirt"]})
    }


def test_merge_extra():
    pack = DataPack()
    pack.merge(DataPack(description="hello", pack_format=88))
    assert pack.description == "hello"
    assert pack.pack_format == 88


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

    assert custom.functions.match() == set()

    assert custom.functions.match("*") == set(funcs) | {
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

    assert pack.functions.match() == set()

    assert pack.functions.match("*") == set(custom_funcs) | set(hey_funcs) | {
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


def test_overload_proxy():
    pack = DataPack()
    pack["demo:foo"] = Function(["say foo"])
    assert pack[Function]["demo:foo"] is pack.functions["demo:foo"]


def test_accessors_with_function(tmp_path: Path):
    func1 = Function(["say hello"])

    assert func1._content == ["say hello"]  # type: ignore

    assert func1.lines == ["say hello"]
    assert func1._content == func1.lines  # type: ignore

    assert func1.text == "say hello\n"
    assert func1._content == "say hello\n"  # type: ignore

    filename = tmp_path / "foo.mcfunction"
    filename.write_text("say world")
    func2 = Function(source_path=filename)

    assert func2._content is None  # type: ignore

    assert func2.text == "say world"
    assert func2._content == func2.text  # type: ignore
    assert func2.source_path is None

    assert func2.lines == ["say world"]
    assert func2._content == func2.lines  # type: ignore

    assert func2.text == "say world\n"
    assert func2._content == func2.text  # type: ignore


def test_on_bind():
    def on_bind_callback(instance: Function, pack: DataPack, path: str):
        pack[path + "_alias"] = Function([f"function {path}"])

    pack = DataPack()
    pack["hello:world"] = Function(
        ["say hello"], tags=["minecraft:load"], on_bind=on_bind_callback
    )

    assert pack.functions == {
        "hello:world": Function(["say hello"]),
        "hello:world_alias": Function(["function hello:world"]),
    }

    assert pack.function_tags == {
        "minecraft:load": FunctionTag({"values": ["hello:world"]})
    }


def test_on_bind_rename():
    @dataclass
    class RenameTo:
        name: str

        def __call__(self, instance: Function, pack: DataPack, path: str):
            if path != self.name:
                pack[self.name] = instance
                raise Drop()

    pack = DataPack()
    pack["hello:world"] = Function(
        ["say hello"], tags=["minecraft:load"], on_bind=RenameTo("hello:other")
    )

    assert pack == {
        "hello": {Function: {"other": Function(["say hello"])}},
        "minecraft": {FunctionTag: {"load": FunctionTag({"values": ["hello:other"]})}},
    }


def test_merge_rules():
    def combine_description(
        pack: DataPack,
        path: str,
        current: JsonFile,
        conflict: JsonFile,
    ) -> bool:
        current.data["pack"]["description"] += conflict.data["pack"]["description"]
        return True

    pack = DataPack(description="hello")
    pack.merge_policy.extend_extra("pack.mcmeta", combine_description)

    pack.merge(DataPack(description="world"))

    assert pack.description == "helloworld"


def test_merge_nuke():
    def nuke(*args: Any) -> bool:
        raise Drop()

    p1 = DataPack(
        description="hello",
        merge_policy=MergePolicy(extra={"pack.mcmeta": [nuke]}),
    )

    p1.merge_policy.extend(MergePolicy(namespace={Function: [nuke]}))
    p1.merge_policy.extend_namespace_extra("foo.json", nuke)

    p1["demo:foo"] = Function()
    p1["demo"].extra["foo.json"] = JsonFile()
    p1["thing"].extra["foo.json"] = JsonFile()

    p2 = DataPack(description="world")
    p2["demo:foo"] = Function()
    p2["demo:bar"] = Function()
    p2["demo"].extra["foo.json"] = JsonFile()

    p1.merge(p2)

    assert p1.description == ""
    assert list(p1.functions) == ["demo:bar"]
    assert list(p1["demo"].extra) == []
    assert p1["thing"].extra["foo.json"] == JsonFile()


def test_merge_filter():
    p1 = DataPack(filter={"block": [{"namespace": "foo"}]})
    p2 = DataPack(filter={"block": [{"namespace": "bar"}]})
    p1.merge(p2)

    assert p1.filter == {"block": [{"namespace": "foo"}, {"namespace": "bar"}]}

    p1.merge(p2)
    assert p1.filter == {"block": [{"namespace": "foo"}, {"namespace": "bar"}]}

    p3 = DataPack()
    p3.filter["block"].append({"namespace": "thing"})

    p1.merge(p3)

    assert p1.filter == {
        "block": [{"namespace": "foo"}, {"namespace": "bar"}, {"namespace": "thing"}]
    }


def test_select():
    p = DataPack()
    p["demo:foo"] = Function()
    p["demo:bar"] = Function()
    p["demo:some_loot"] = LootTable()
    p["demo:some_other_loot"] = LootTable()
    p["minecraft:default_loot"] = LootTable()
    p["minecraft:tick"] = FunctionTag()
    p["minecraft:load"] = FunctionTag()
    p["other_namespace:what/is/that"] = BlockTag()

    assert select_files(p, ".mcfunction", files=r".*") == {
        p.functions["demo:foo"]: ("data/demo/functions/foo.mcfunction", None),
        p.functions["demo:bar"]: ("data/demo/functions/bar.mcfunction", None),
    }
    assert select_files(p, extend=Function, files=r".*") == {
        p.functions["demo:foo"]: ("data/demo/functions/foo.mcfunction", None),
        p.functions["demo:bar"]: ("data/demo/functions/bar.mcfunction", None),
    }
    assert select_files(p, ".mcfunction", match="*") == {
        p.functions["demo:foo"]: (None, "demo:foo"),
        p.functions["demo:bar"]: (None, "demo:bar"),
    }
    assert select_files(p, extend=Function, match="*") == {
        p.functions["demo:foo"]: (None, "demo:foo"),
        p.functions["demo:bar"]: (None, "demo:bar"),
    }
    assert select_files(p, match={"function": "*"}) == {
        p.functions["demo:foo"]: (None, "demo:foo"),
        p.functions["demo:bar"]: (None, "demo:bar"),
    }
    assert select_files(p, match={"functions": "*"}) == {
        p.functions["demo:foo"]: (None, "demo:foo"),
        p.functions["demo:bar"]: (None, "demo:bar"),
    }

    assert select_files(p, files=r"^pack\.mcmeta$") == {
        p.mcmeta: ("pack.mcmeta", None),
    }
    assert select_files(p, ".mcmeta", files=r".*") == {
        p.mcmeta: ("pack.mcmeta", None),
    }
    assert select_files(p, extend=Mcmeta, files=r".*") == {
        p.mcmeta: ("pack.mcmeta", None),
    }
    assert select_files(p, extend=Mcmeta, match="*") == {}

    assert set(select_files(p, files=r".*\.json")) == {
        p.loot_tables["demo:some_loot"],
        p.loot_tables["demo:some_other_loot"],
        p.loot_tables["minecraft:default_loot"],
        p.function_tags["minecraft:tick"],
        p.function_tags["minecraft:load"],
        p.block_tags["other_namespace:what/is/that"],
    }
    assert set(select_files(p, files=r"data/minecraft/.*\.json")) == {
        p.loot_tables["minecraft:default_loot"],
        p.function_tags["minecraft:tick"],
        p.function_tags["minecraft:load"],
    }
    assert set(select_files(p, ".json", match=r"minecraft:*")) == {
        p.loot_tables["minecraft:default_loot"],
        p.function_tags["minecraft:tick"],
        p.function_tags["minecraft:load"],
    }
    assert set(select_files(p, extend=JsonFileBase[Any], match=r"minecraft:*")) == {
        p.loot_tables["minecraft:default_loot"],
        p.function_tags["minecraft:tick"],
        p.function_tags["minecraft:load"],
    }
    assert set(select_files(p, extend=JsonFileBase[Any], files=r".*")) == {
        p.mcmeta,
        p.loot_tables["demo:some_loot"],
        p.loot_tables["demo:some_other_loot"],
        p.loot_tables["minecraft:default_loot"],
        p.function_tags["minecraft:tick"],
        p.function_tags["minecraft:load"],
        p.block_tags["other_namespace:what/is/that"],
    }

    assert set(select_files(p, files=[r".*loot\.json", r"pack\.mcmeta"])) == {
        p.mcmeta,
        p.loot_tables["demo:some_loot"],
        p.loot_tables["demo:some_other_loot"],
        p.loot_tables["minecraft:default_loot"],
    }
    assert set(
        select_files(p, files={"regex": r".*LoOt.*", "flags": "IGNORECASE"})
    ) == {
        p.loot_tables["demo:some_loot"],
        p.loot_tables["demo:some_other_loot"],
        p.loot_tables["minecraft:default_loot"],
    }
    assert set(select_files(p, match=["minecraft:*", "demo:*", "!*other*"])) == {
        p.functions["demo:foo"],
        p.functions["demo:bar"],
        p.loot_tables["demo:some_loot"],
        p.loot_tables["minecraft:default_loot"],
        p.function_tags["minecraft:tick"],
        p.function_tags["minecraft:load"],
    }


def test_overlay():
    p = DataPack()
    assert not p.overlays

    a = p.overlays["a"]
    assert a.overlay_name == "a"
    assert a.overlay_parent is p

    assert p == DataPack()
    assert a == DataPack()
    assert a == p
    assert not p
    assert not a

    a["demo:foo"] = Function(["say hello"])

    assert p != DataPack()
    assert a != DataPack()
    assert a != p
    assert p
    assert a

    assert a.supported_formats is None
    assert p.mcmeta.data == {"pack": {"pack_format": 18, "description": ""}}

    a.supported_formats = [17, 18]
    assert p.mcmeta.data == {
        "pack": {"pack_format": 18, "description": ""},
        "overlays": {"entries": [{"formats": [17, 18], "directory": "a"}]},
    }

    b = p.overlays.setdefault(
        "b", supported_formats={"min_inclusive": 16, "max_inclusive": 17}
    )
    assert b.supported_formats == {"min_inclusive": 16, "max_inclusive": 17}
    assert p.mcmeta.data == {
        "pack": {"pack_format": 18, "description": ""},
        "overlays": {
            "entries": [
                {
                    "formats": [17, 18],
                    "directory": "a",
                },
                {
                    "formats": {"min_inclusive": 16, "max_inclusive": 17},
                    "directory": "b",
                },
            ]
        },
    }

    assert p.overlays.setdefault("b", supported_formats=18) is b
    assert b.supported_formats == {"min_inclusive": 16, "max_inclusive": 17}

    c = DataPack(supported_formats=19)
    c["demo:thing"] = Function()
    p.overlays["c"] = c

    assert c.overlay_name == "c"
    assert c.overlay_parent is p
    assert dict(p.list_files()) == {
        "a/data/demo/functions/foo.mcfunction": Function(["say hello"]),
        "c/data/demo/functions/thing.mcfunction": Function([]),
        "pack.mcmeta": Mcmeta(
            {
                "pack": {"pack_format": 18, "description": ""},
                "overlays": {
                    "entries": [
                        {
                            "formats": [17, 18],
                            "directory": "a",
                        },
                        {
                            "formats": {"min_inclusive": 16, "max_inclusive": 17},
                            "directory": "b",
                        },
                        {
                            "formats": 19,
                            "directory": "c",
                        },
                    ]
                },
            }
        ),
    }

    del p.overlays["b"]
    assert p.mcmeta.data == {
        "pack": {"pack_format": 18, "description": ""},
        "overlays": {
            "entries": [
                {
                    "formats": [17, 18],
                    "directory": "a",
                },
                {
                    "formats": 19,
                    "directory": "c",
                },
            ]
        },
    }

    q = DataPack()
    q.overlays["stuff"]["demo:stuff"] = Function(["say stuff"])
    p.merge(q)

    assert p.overlays["stuff"].overlay_parent is p
    assert p.overlays["stuff"].functions["demo:stuff"] == Function(["say stuff"])
    assert p.overlays["stuff"].supported_formats is None

    assert p.overlays["bingo"].overlays is p.overlays

    d = DataPack()
    d["demo:init"] = Function(["say original init"])
    d.overlays["bop"]["demo:init"] = Function(["say init"])
    d.overlays.setdefault("bop2", supported_formats=99)["demo:init"] = Function()
    p.overlays["d"] = d

    assert p.overlays["d"].overlays is p.overlays
    assert p.overlays["bop"].overlays is p.overlays
    assert p.overlays["bop2"].overlays is p.overlays
    assert p.overlays["d"].functions["demo:init"] == Function(["say original init"])
    assert p.overlays["bop"].functions["demo:init"] == Function(["say init"])
    assert p.overlays["bop2"].functions["demo:init"] == Function()
