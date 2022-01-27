from pathlib import Path

import pytest
from beet import Context, Function, run_beet
from pytest_insta import SnapshotFixture

from mecha import AstNode, CompilationDatabase, CompilationUnit, DiagnosticError, Mecha
from mecha.contrib.annotate_diagnostics import annotate_diagnostics
from mecha.contrib.bolt import Runtime

BOLT_EXAMPLES = [
    Function(source)
    for source in Path("tests/resources/bolt_examples.mcfunction")
    .read_text()
    .split("###\n")
]


@pytest.fixture(scope="session")
def ctx_bolt():
    with run_beet({"require": ["mecha.contrib.bolt"]}) as ctx:
        yield ctx


@pytest.mark.parametrize(
    "source",
    params := BOLT_EXAMPLES,
    ids=range(len(params)),
)
def test_parse(snapshot: SnapshotFixture, ctx_bolt: Context, source: Function):
    mc = ctx_bolt.inject(Mecha)
    runtime = ctx_bolt.inject(Runtime)

    ast = None
    diagnostics = None

    try:
        ast = mc.parse(source)
    except DiagnosticError as exc:
        diagnostics = exc.diagnostics

    if ast:
        assert snapshot() == f"{source.text}---\n{ast.dump()}\n"
        text, output, refs = runtime.codegen(ast)
        text = text or "# Nothing\n"
        assert snapshot() == f"{text}---\noutput = {output}\n---\n" + "".join(
            f"_mecha_refs[{i}]\n{obj.dump(shallow=True) if isinstance(obj, AstNode) else repr(obj)}\n"
            for i, obj in enumerate(refs)
        )
    elif diagnostics:
        database = CompilationDatabase()
        database[source] = CompilationUnit(source=source.text)
        annotate_diagnostics(database, diagnostics)
        assert snapshot() == source.text
