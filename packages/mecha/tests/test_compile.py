from dataclasses import replace
from typing import Any

import pytest
from beet import DataPack, Function, TextFile

from mecha import (
    AstChildren,
    AstCommand,
    AstJsonValue,
    AstMessage,
    AstMessageText,
    AstSelector,
    Diagnostic,
    DiagnosticCollection,
    DiagnosticError,
    Mecha,
    rule,
)


@rule(AstCommand, identifier="say:message")
def convert_say_to_tellraw(node: AstCommand):
    if isinstance(message := node.arguments[0], AstMessage):
        return replace(
            node,
            identifier="tellraw:targets:message",
            arguments=AstChildren(
                [
                    AstSelector(variable="a"),
                    AstJsonValue(
                        value="".join(
                            f.value
                            for f in message.fragments
                            if isinstance(f, AstMessageText)
                        )
                    ),
                ],
            ),
        )


@pytest.fixture
def dummy_transform(mc: Mecha):
    mc.transform.extend(convert_say_to_tellraw)
    yield
    mc.transform.reset()


def test_string(mc: Mecha, dummy_transform: Any):
    function = mc.compile("say hello world")
    assert function.text == 'tellraw @a "hello world"\n'

    compilation_unit = mc.database[function]

    ast = compilation_unit.ast
    assert ast == mc.parse(function.text)
    assert compilation_unit.source == "say hello world"
    assert compilation_unit.filename is None
    assert compilation_unit.resource_location is None
    assert not compilation_unit.diagnostics.exceptions


def test_list(mc: Mecha, dummy_transform: Any):
    function = mc.compile(["say hello world"])
    assert function.text == 'tellraw @a "hello world"\n'

    compilation_unit = mc.database[function]

    ast = compilation_unit.ast
    assert ast == mc.parse(function.text)
    assert compilation_unit.source == "say hello world\n"
    assert compilation_unit.filename is None
    assert compilation_unit.resource_location is None
    assert not compilation_unit.diagnostics.exceptions


def test_file(mc: Mecha, dummy_transform: Any):
    input_file = TextFile("say hello world")
    function = mc.compile(input_file)
    assert function is input_file
    assert function.text == 'tellraw @a "hello world"\n'

    compilation_unit = mc.database[function]

    ast = compilation_unit.ast
    assert ast == mc.parse(function.text)
    assert compilation_unit.source == "say hello world"
    assert compilation_unit.filename is None
    assert compilation_unit.resource_location is None
    assert not compilation_unit.diagnostics.exceptions


def test_ast(mc: Mecha, dummy_transform: Any):
    ast = mc.parse("say hello world")
    function = mc.compile(ast)
    assert function.text == 'tellraw @a "hello world"\n'

    compilation_unit = mc.database[function]

    ast = compilation_unit.ast
    assert ast == mc.parse(function.text)
    assert compilation_unit.source is None
    assert compilation_unit.filename is None
    assert compilation_unit.resource_location is None
    assert not compilation_unit.diagnostics.exceptions


def test_data_pack(mc: Mecha, dummy_transform: Any):
    pack = DataPack()
    pack["demo:foo"] = Function("say hello world")

    result = mc.compile(pack)
    assert result is pack

    function = pack.functions["demo:foo"]
    assert function.text == 'tellraw @a "hello world"\n'

    compilation_unit = mc.database[function]

    ast = compilation_unit.ast
    assert ast == mc.parse(function.text)
    assert compilation_unit.source == "say hello world"
    assert compilation_unit.filename is None
    assert compilation_unit.resource_location == "demo:foo"
    assert not compilation_unit.diagnostics.exceptions

    assert mc.database.index["demo:foo"] is function


@rule(AstCommand, identifier="say:message")
def do_not_use_say(node: AstCommand):
    raise Diagnostic("warn", "Do not use the say command.")


@pytest.fixture
def dummy_lint(mc: Mecha):
    mc.lint.extend(do_not_use_say)
    yield
    mc.lint.reset()


def test_lint_warn(mc: Mecha, dummy_transform: Any, dummy_lint: Any):
    function = mc.compile("say hello world")
    assert function.text == 'tellraw @a "hello world"\n'

    d = mc.database[function].diagnostics.exceptions[0]
    assert d.level == "warn"
    assert d.format_message() == "Do not use the say command. (do_not_use_say)"


@rule(AstCommand, identifier="say:message")
def really_do_not_use_say(node: AstCommand):
    raise Diagnostic("error", "Really don't.")


@pytest.fixture
def dummy_lint_error(mc: Mecha):
    mc.lint.extend(really_do_not_use_say)
    yield
    mc.lint.reset()


def test_lint_error(mc: Mecha, dummy_transform: Any, dummy_lint_error: Any):
    with pytest.raises(DiagnosticError) as exc_info:
        mc.compile("say hello world")

    d = exc_info.value.diagnostics.exceptions[0]
    assert d.level == "error"
    assert d.format_message() == "Really don't. (really_do_not_use_say)"


def test_lint_error_report(mc: Mecha, dummy_transform: Any, dummy_lint_error: Any):
    diagnostics = DiagnosticCollection()

    function = mc.compile("say hello world", report=diagnostics)
    assert function.text == "say hello world"

    d = mc.database[function].diagnostics.exceptions[0]
    assert d.level == "error"
    assert d.format_message() == "Really don't. (really_do_not_use_say)"
