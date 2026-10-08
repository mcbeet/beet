# AI-assisted (Claude, Anthropic): see the commit message.
from pathlib import Path

import pytest
from beet import DataPack, Function

from mecha import DiagnosticError, Mecha


def test_compile_reports_undecodable_function(mc: Mecha, tmp_path: Path):
    path = tmp_path / "broken.mcfunction"
    path.write_bytes(b"say \xff\xfe\n")

    pack = DataPack()
    pack["demo:broken"] = Function(source_path=path)
    pack["demo:fine"] = Function("say fine\n")

    with pytest.raises(DiagnosticError) as exc_info:
        mc.compile(pack)

    errors = list(exc_info.value.diagnostics.get_all_errors())
    assert len(errors) == 1
    assert "utf-8" in errors[0].message
    assert errors[0].hint == "demo:broken"
