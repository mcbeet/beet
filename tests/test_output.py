import os
import subprocess
import sys
from pathlib import Path

import pytest

from beet import DataPack, Function
from beet.contrib.output import incremental_save


def function_pack(function: Function) -> DataPack:
    pack = DataPack()
    pack["demo:a"] = function
    return pack


def test_newline_change_rewrites(tmp_path: Path):
    out, manifest = tmp_path / "out", tmp_path / "manifest.json"
    incremental_save(function_pack(Function("say a\n", newline="\r\n")), out, manifest)
    incremental_save(function_pack(Function("say a\n", newline="\n")), out, manifest)
    assert (out / "data/demo/function/a.mcfunction").read_bytes() == b"say a\n"


def test_compare_sees_line_endings(tmp_path: Path):
    disk = tmp_path / "out/data/demo/function/a.mcfunction"
    disk.parent.mkdir(parents=True)
    disk.write_bytes(b"say a\r\n")
    incremental_save(function_pack(Function("say a\n", newline="\n")), tmp_path / "out")
    assert disk.read_bytes() == b"say a\n"


def test_switching_source_with_same_stat(tmp_path: Path):
    out, manifest = tmp_path / "out", tmp_path / "manifest.json"
    first, second = tmp_path / "first.mcfunction", tmp_path / "second.mcfunction"
    first.write_text("say 1\n")
    second.write_text("say 2\n")
    stat = first.stat()
    os.utime(second, ns=(stat.st_atime_ns, stat.st_mtime_ns))

    incremental_save(function_pack(Function(source_path=first)), out, manifest)
    incremental_save(function_pack(Function(source_path=second)), out, manifest)
    assert (out / "data/demo/function/a.mcfunction").read_text() == "say 2\n"


def test_hard_link_target_untouched(tmp_path: Path):
    source = tmp_path / "source.mcfunction"
    source.write_text("user source\n")
    disk = tmp_path / "out/data/demo/function/a.mcfunction"
    disk.parent.mkdir(parents=True)
    os.link(source, disk)

    incremental_save(function_pack(Function("compiled\n")), tmp_path / "out")
    assert source.read_text() == "user source\n"
    assert disk.read_text() == "compiled\n"


def test_symlink_target_untouched(tmp_path: Path):
    source = tmp_path / "source.mcfunction"
    source.write_text("user source\n")
    disk = tmp_path / "out/data/demo/function/a.mcfunction"
    disk.parent.mkdir(parents=True)
    try:
        disk.symlink_to(source)
    except OSError:
        pytest.skip("Symlinks need extra privileges on this system")

    incremental_save(function_pack(Function("compiled\n")), tmp_path / "out")
    assert source.read_text() == "user source\n"
    assert not disk.is_symlink()


@pytest.mark.skipif(sys.platform != "win32", reason="Junctions only exist on Windows")
def test_junction_target_untouched(tmp_path: Path):
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    (elsewhere / "precious.txt").write_text("keep me")
    (tmp_path / "out/data").mkdir(parents=True)
    junction = tmp_path / "out/data/linked"
    subprocess.run(
        ["cmd", "/c", "mklink", "/J", junction, elsewhere],
        check=True,
        capture_output=True,
    )

    incremental_save(function_pack(Function("say a\n")), tmp_path / "out")
    assert (elsewhere / "precious.txt").exists()
    assert not junction.exists()
