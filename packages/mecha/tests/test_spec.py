from pytest_insta import SnapshotFixture

from mecha import CommandArgument, Mecha


def test_prototypes(snapshot: SnapshotFixture, mc: Mecha):
    assert snapshot("json") == list(mc.spec.prototypes)


def test_parsers(snapshot: SnapshotFixture, mc: Mecha):
    all_defined_parsers = {
        parser[17:]
        for parser in mc.spec.parsers
        if parser.startswith("command:argument:")
    }

    all_used_parser = {
        tree.parser
        for prototype in mc.spec.prototypes.values()
        for argument in prototype.signature
        if isinstance(argument, CommandArgument)
        if (tree := mc.spec.tree.get(argument.scope))
        if tree.parser
    }

    undefined_parsers = all_used_parser - all_defined_parsers

    assert not undefined_parsers


def test_repr(snapshot: SnapshotFixture, mc: Mecha):
    assert (
        str(mc.spec.tree.get("execute", "if", "score"))
        == "CommandTree(type='literal', children={'target': ...})"
    )

    assert (
        str(mc.spec.tree.get("execute", "if", "score", "target"))
        == "CommandTree(type='argument', parser='minecraft:score_holder', properties={'amount': 'single'}, children={'targetObjective': ...})"
    )
