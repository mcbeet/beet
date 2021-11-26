import pytest
from beet import Function, run_beet
from pytest_insta import SnapshotFixture

from mecha import (
    CompilationDatabase,
    CompilationUnit,
    DiagnosticError,
    Mecha,
    get_scripting_examples,
)
from mecha.contrib.annotate_diagnostics import annotate_diagnostics


@pytest.fixture(scope="session")
def mc_scripting():
    with run_beet({"require": ["mecha.contrib.scripting"]}) as ctx:
        yield ctx.inject(Mecha)


@pytest.mark.parametrize(
    "source",
    params := get_scripting_examples(),
    ids=range(len(params)),
)
def test_parse(snapshot: SnapshotFixture, mc_scripting: Mecha, source: Function):
    ast = None
    diagnostics = None

    try:
        ast = mc_scripting.parse(source)
    except DiagnosticError as exc:
        diagnostics = exc.diagnostics

    if ast:
        assert snapshot() == ast.dump() + "\n"
    elif diagnostics:
        database = CompilationDatabase()
        database[source] = CompilationUnit(source=source.text)
        annotate_diagnostics(database, diagnostics)
        assert snapshot() == source.text
