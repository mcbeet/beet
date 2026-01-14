from pathlib import Path

import pytest
from beet import Context, Function
from beet.core.utils import format_exc
from mecha import CompilationError, DiagnosticError, Mecha
from pytest_insta import SnapshotFixture

SANDBOX_EXAMPLES = [
    Function(source)
    for source in Path("tests/resources/sandbox_examples.mcfunction")
    .read_text()
    .split("###\n")
]


@pytest.mark.parametrize(
    "source",
    params := SANDBOX_EXAMPLES,
    ids=range(len(params)),
)
def test_run(snapshot: SnapshotFixture, ctx_sandbox: Context, source: Function):
    mc = ctx_sandbox.inject(Mecha)

    with pytest.raises((CompilationError, DiagnosticError)) as exc_info:
        mc.compile(source, resource_location="demo:foo")

    details = (
        format_exc(exc_info.value.__cause__)
        if isinstance(exc_info.value, CompilationError)
        else str(exc_info.value)
    )
    assert snapshot() == f"{source.text}---\n{details}"
