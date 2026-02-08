import pytest
from beet import Function, JsonFile
from beet.core.utils import JsonDict
from pytest_insta import SnapshotFixture

from mecha import DiagnosticError, Mecha

MULTIPLE_ERRORS = Function(source_path="tests/resources/multiple_errors.mcfunction")
COMMAND_EXAMPLES = Function(source_path="tests/resources/command_examples.mcfunction")
MULTILINE_COMMAND_EXAMPLES = Function(
    source_path="tests/resources/multiline_command_examples.mcfunction"
)
ARGUMENT_EXAMPLES = JsonFile(source_path="tests/resources/argument_examples.json")


def test_command_examples(snapshot: SnapshotFixture, mc: Mecha):
    ast = mc.parse(COMMAND_EXAMPLES)
    assert snapshot() == ast.dump()
    assert snapshot() == mc.serialize(ast)


def test_multiline_command_examples(snapshot: SnapshotFixture, mc: Mecha):
    ast = mc.parse(MULTILINE_COMMAND_EXAMPLES, multiline=True)
    assert snapshot() == ast.dump()
    assert snapshot() == mc.serialize(ast)


@pytest.mark.parametrize(
    "test_name, properties, invalid, value",
    params := [
        (
            f"{argument_parser} {i} {j}",
            suite.get("properties", {}),
            suite.get("invalid", False),
            value,
        )
        for argument_parser, suites in ARGUMENT_EXAMPLES.data.items()
        for i, suite in enumerate(suites)
        for j, value in enumerate(suite["examples"])
    ],
    ids=[args[0] for args in params],
)
def test_argument_examples(
    snapshot: SnapshotFixture,
    mc: Mecha,
    test_name: str,
    properties: JsonDict,
    invalid: bool,
    value: str,
):
    argument_parser = f"command:argument:{test_name.partition(' ')[0]}"
    if argument_parser not in mc.spec.parsers:
        pytest.skip()

    if invalid:
        with pytest.raises(DiagnosticError) as exc_info:
            mc.parse(value, using=argument_parser, provide={"properties": properties})
        assert snapshot() == "\n---\n".join(
            [
                test_name,
                str(properties),
                value,
                str(exc_info.value),
            ]
        )
    else:
        ast = mc.parse(value, using=argument_parser, provide={"properties": properties})
        assert snapshot() == "\n---\n".join(
            [test_name, str(properties), value, mc.serialize(ast), ast.dump()]
        )


def test_multiline(snapshot: SnapshotFixture, mc: Mecha):
    function = """
        execute
            as @a                        # For each "player",
            at @s                        # start at their feet.
            anchored eyes                # Looking through their eyes,
            facing 0 0 0                 # face perfectly at the target
            anchored feet                # (go back to the feet)
            positioned ^ ^ ^1            # and move one block forward.
            rotated as @s                # Face the direction the player
                                         # is actually facing,
            positioned ^ ^ ^-1           # and move one block back.
            if entity @s[distance=..0.6] # Check if we're close to the
                                         # player's feet.
            run
                say I'm facing the target!
    """

    ast = mc.parse(function, multiline=True)

    assert snapshot() == ast.dump()
    assert snapshot() == mc.serialize(ast)


def test_say(snapshot: SnapshotFixture, mc: Mecha):
    function = """
        say hello @s world
            say thing
    """

    ast = mc.parse(function)
    ast_multiline = mc.parse(function, multiline=True)

    assert snapshot() == ast.dump()
    assert snapshot() == ast_multiline.dump()

    assert snapshot() == mc.serialize(ast)
    assert snapshot() == mc.serialize(ast_multiline)


def test_player_name(mc_1_17: Mecha):
    with pytest.raises(DiagnosticError) as exc_info:
        mc_1_17.parse(
            "scoreboard players set some_really_long_name_right_here_but_its_actually_even_longer foo 42"
        )
    assert (
        str(exc_info.value)
        == "Reported 1 error.\n\nline 1, column 24: Expected up to 40 characters."
    )


def test_player_name_no_length_restriction(mc: Mecha):
    assert (
        mc.serialize(
            mc.parse("scoreboard players set some_really_long_name_right_here foo 42")
        )
        == "scoreboard players set some_really_long_name_right_here foo 42\n"
    )


def test_multiple_parse_errors(mc: Mecha):
    with pytest.raises(DiagnosticError) as exc_info:
        res = mc.parse(MULTIPLE_ERRORS, multiline=True)

    assert len(exc_info.value.diagnostics.exceptions) > 1


if __name__ == "__main__":
    Mecha().parse(MULTIPLE_ERRORS, multiline=True)
