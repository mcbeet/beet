import json
from pathlib import Path

from beet import DataPack, Function, FunctionTag, Project


def build_data_pack(path: Path, config: dict):
    path.write_text(json.dumps(config))
    ctx = Project.from_config(path).build()
    ctx.data.load(eager=True)
    return ctx.data


def test_load_other_data_packs(tmp_path):
    with DataPack(path=tmp_path / "foo") as p1:
        p1["foo:thing"] = Function(["say foo"], tags=["minecraft:load"])

    with DataPack(path=tmp_path / "bar") as p2:
        p2["bar:thing"] = Function(["say bar"], tags=["minecraft:load"])

    data = build_data_pack(
        tmp_path / "beet.json",
        {"meta": {"load": {"data_packs": [str(p1.path), str(p2.path)]}}},
    )

    assert data.functions == {
        "foo:thing": Function(["say foo"]),
        "bar:thing": Function(["say bar"]),
    }

    assert data.function_tags == {
        "minecraft:load": FunctionTag({"values": ["foo:thing", "bar:thing"]})
    }


def test_function_preamble(tmp_path):
    with DataPack(path=tmp_path / "foo") as p1:
        p1["foo:thing"] = Function(["say foo"])

    data = build_data_pack(
        tmp_path / "beet.json",
        {
            "meta": {
                "load": {"data_packs": [str(p1.path)]},
                "preamble": {"template": "# {function_name}"},
            }
        },
    )

    assert data.functions == {"foo:thing": Function(["# foo:thing", "", "say foo"])}
