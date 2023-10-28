from pathlib import Path
from random import Random
from uuid import UUID

import pytest
from beet import Context, Function
from mecha import AstNode, CompilationDatabase, CompilationUnit, DiagnosticError, Mecha
from mecha.contrib.annotate_diagnostics import annotate_diagnostics
from pytest_insta import SnapshotFixture

from bolt import Runtime

BOLT_EXAMPLES = [
    Function(source)
    for source in Path("tests/resources/bolt_examples.mcfunction")
    .read_text()
    .split("###\n")
]


@pytest.mark.parametrize(
    "source",
    params := BOLT_EXAMPLES,
    ids=range(len(params)),
)
def test_parse(snapshot: SnapshotFixture, ctx: Context, source: Function):
    mc = ctx.inject(Mecha)
    runtime = ctx.inject(Runtime)

    ast = None
    diagnostics = None

    mc.database.current = source
    mc.database[source] = CompilationUnit(resource_location="demo:test")

    rand = Random()
    rand.seed(42)

    try:
        ast = mc.parse(
            source, provide={"uuid_factory": lambda: UUID(int=rand.getrandbits(128))}
        )
    except DiagnosticError as exc:
        diagnostics = exc.diagnostics
    finally:
        del mc.database[mc.database.current]

    if ast:
        assert snapshot() == f"{source.text}---\n{ast.dump()}\n"
        result = runtime.modules.codegen(ast)
        text = result.source or "# Nothing\n"
        assert snapshot() == f"{text}---\noutput = {result.output}\n---\n" + "".join(
            f"_bolt_refs[{i}]\n{obj.dump(shallow=True) if isinstance(obj, AstNode) else repr(obj)}\n"
            for i, obj in enumerate(result.refs)
        )
    elif diagnostics:
        database = CompilationDatabase()
        database[source] = CompilationUnit(source=source.text)
        annotate_diagnostics(database, diagnostics)
        assert snapshot() == source.text
