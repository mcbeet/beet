# AI-assisted (Claude, Anthropic): see the commit message.
import json
import subprocess
import sys
from pathlib import Path


def run_mecha(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "mecha", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def test_json_output_without_stats_flag(tmp_path: Path):
    (tmp_path / "foo.mcfunction").write_text("say hello\n")

    result = run_mecha(tmp_path, "-j", "stats.json", "foo.mcfunction")

    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads((tmp_path / "stats.json").read_text())
    assert data["function_count"] == 1


def test_json_output_with_stats_flag(tmp_path: Path):
    (tmp_path / "foo.mcfunction").write_text("say hello\n")

    result = run_mecha(tmp_path, "-s", "-j", "stats.json", "foo.mcfunction")

    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads((tmp_path / "stats.json").read_text())["function_count"] == 1


def test_no_json_file_without_json_flag(tmp_path: Path):
    (tmp_path / "foo.mcfunction").write_text("say hello\n")

    result = run_mecha(tmp_path, "foo.mcfunction")

    assert result.returncode == 0, result.stdout + result.stderr
    assert list(tmp_path.glob("*.json")) == []


def test_undecodable_file_is_reported_without_traceback(tmp_path: Path):
    (tmp_path / "foo.mcfunction").write_bytes(b"say \xff\xfe\n")

    result = run_mecha(tmp_path, "foo.mcfunction")
    output = result.stdout + result.stderr

    assert result.returncode == 1, output
    assert "as utf-8" in output
    assert "foo.mcfunction" in output
    assert "Traceback" not in output


def test_undecodable_file_does_not_stop_directory_validation(tmp_path: Path):
    functions = tmp_path / "functions"
    functions.mkdir()
    (functions / "a.mcfunction").write_bytes(b"say \xff\xfe\n")
    (functions / "b.mcfunction").write_text("say ok\nfoo bar\n")
    (functions / "c.mcfunction").write_text("say fine\n")

    result = run_mecha(tmp_path, "functions")
    output = result.stdout + result.stderr

    assert result.returncode == 1, output
    assert "Reported 2 errors" in output
    assert "Traceback" not in output


def test_invalid_minecraft_version_is_a_usage_error(tmp_path: Path):
    (tmp_path / "foo.mcfunction").write_text("say hello\n")

    result = run_mecha(tmp_path, "-m", "abc", "foo.mcfunction")
    output = result.stdout + result.stderr

    assert result.returncode == 2, output
    assert "is not a valid Minecraft version" in output
    assert "Traceback" not in output


def test_valid_minecraft_version(tmp_path: Path):
    (tmp_path / "foo.mcfunction").write_text("say hello\n")

    result = run_mecha(tmp_path, "-m", "1.20", "foo.mcfunction")

    assert result.returncode == 0, result.stdout + result.stderr


def test_undecodable_function_in_data_pack_is_reported_per_file(tmp_path: Path):
    pack = tmp_path / "pack"
    (pack / "data" / "demo" / "function").mkdir(parents=True)
    (pack / "pack.mcmeta").write_text(
        '{"pack": {"pack_format": 48, "description": "test"}}'
    )
    (pack / "data" / "demo" / "function" / "broken.mcfunction").write_bytes(
        b"say \xff\xfe\n"
    )
    (pack / "data" / "demo" / "function" / "bad.mcfunction").write_text(
        "say ok\nfoo bar\n"
    )
    (pack / "data" / "demo" / "function" / "fine.mcfunction").write_text("say fine\n")

    result = run_mecha(tmp_path, "pack")
    output = result.stdout + result.stderr

    assert result.returncode == 1, output
    assert "pack/data/demo/function/broken.mcfunction" in output
    assert "Reported 2 errors" in output
    assert "Traceback" not in output
