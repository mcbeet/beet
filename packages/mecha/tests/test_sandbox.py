from pathlib import Path

import pytest
from beet import Context, Function, run_beet
from beet.toolchain.utils import format_exc
from pytest_insta import SnapshotFixture

from mecha import CompilationError, Mecha

SANDBOX_EXAMPLES = [
    Function(source)
    for source in Path("tests/resources/sandbox_examples.mcfunction")
    .read_text()
    .split("###\n")
]


@pytest.fixture(scope="session")
def ctx_sandbox():
    with run_beet({"require": ["mecha.contrib.scripting_sandbox"]}) as ctx:
        yield ctx


@pytest.mark.parametrize(
    "source",
    params := SANDBOX_EXAMPLES,
    ids=range(len(params)),
)
def test_run(snapshot: SnapshotFixture, ctx_sandbox: Context, source: Function):
    mc = ctx_sandbox.inject(Mecha)

    with pytest.raises(CompilationError) as exc_info:
        mc.compile(source, resource_location="demo:foo")

    assert snapshot() == f"{source.text}---\n{format_exc(exc_info.value.__cause__)}"  # type: ignore
