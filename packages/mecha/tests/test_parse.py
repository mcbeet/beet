import pytest
from beet.core.utils import JsonDict
from pytest_insta import SnapshotFixture

from mecha import (
    DiagnosticError,
    Mecha,
    get_argument_examples,
    get_command_examples,
    get_multiline_command_examples,
)


def test_command_examples(snapshot: SnapshotFixture, mc: Mecha):
    ast = mc.parse(get_command_examples())
    assert snapshot() == ast.dump()
    assert snapshot() == mc.serialize(ast)


def test_multiline_command_examples(snapshot: SnapshotFixture, mc: Mecha):
    ast = mc.parse(get_multiline_command_examples(), multiline=True)
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
        for argument_parser, suites in get_argument_examples().items()
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


def test_player_name(mc: Mecha):
    with pytest.raises(DiagnosticError) as exc_info:
        mc.parse(
            "scoreboard players set some_really_long_name_right_here_but_its_actually_even_longer foo 42"
        )
    assert (
        str(exc_info.value)
        == "Reported 1 error.\n\nline 1, column 24: Expected up to 40 characters."
    )


def test_player_name_no_length_restriction(mc_1_18: Mecha):
    assert (
        mc_1_18.serialize(
            mc_1_18.parse(
                "scoreboard players set some_really_long_name_right_here foo 42"
            )
        )
        == "scoreboard players set some_really_long_name_right_here foo 42\n"
    )
