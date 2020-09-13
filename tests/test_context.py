from beet import Project, Function, FunctionTag


def test_generate(tmp_path):
    config = tmp_path / "beet.json"
    config.write_text("{}")

    with Project.from_config(config).context() as ctx:
        name1 = ctx.generate(Function(["say hello world"]))
        name2 = ctx.generate(FunctionTag({"values": [name1]}))
        name3 = ctx.generate(Function([f"function #{name2}"]))

    assert [name1, name2, name3] == [
        "beet:generated/function_00000001",
        "beet:generated/functiontag_00000001",
        "beet:generated/function_00000002",
    ]

    assert ctx.data.functions == {
        "beet:generated/function_00000001": Function(["say hello world"]),
        "beet:generated/function_00000002": Function(
            ["function #beet:generated/functiontag_00000001"]
        ),
    }

    assert ctx.data.function_tags == {
        "beet:generated/functiontag_00000001": FunctionTag(
            {"values": ["beet:generated/function_00000001"]}
        ),
    }

    assert ctx.counters == {
        "beet:generated/function_{id:08X}": 2,
        "beet:generated/functiontag_{id:08X}": 1,
    }


def test_generate_custom_template(tmp_path):
    config = tmp_path / "beet.json"
    config.write_text('{"meta": {"generate_template": "foo:{type}_{id}"}}')

    with Project.from_config(config).context() as ctx:
        name = ctx.generate(Function(["say hello world"]))

    assert name == "foo:function_1"
    assert ctx.data.functions == {name: Function(["say hello world"])}


def test_generate_many(tmp_path):
    config = tmp_path / "beet.json"
    config.write_text("{}")

    with Project.from_config(config).context() as ctx:
        for i in range(100):
            ctx.generate(Function([f"say {i}"]))

    assert sorted(ctx.data.functions)[62] == "beet:generated/function_0000003F"
