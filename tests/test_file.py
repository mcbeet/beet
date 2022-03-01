from pathlib import Path

from beet import BinaryFile, TextFile


def test_text_range(tmp_path: Path):
    p1 = tmp_path / "p1"
    p1.write_text("abc")
    assert TextFile(source_path=p1, source_start=1).text == "bc"
    assert TextFile(source_path=p1, source_stop=2).text == "ab"
    assert TextFile(source_path=p1, source_start=1, source_stop=2).text == "b"


def test_binary_range(tmp_path: Path):
    p1 = tmp_path / "p1"
    p1.write_bytes(b"abc")
    assert BinaryFile(source_path=p1, source_start=1).blob == b"bc"
    assert BinaryFile(source_path=p1, source_stop=2).blob == b"ab"
    assert BinaryFile(source_path=p1, source_start=1, source_stop=2).blob == b"b"


def test_original(tmp_path: Path):
    p1 = tmp_path / "p1"
    p1.write_text("abc")
    f = TextFile(source_path=p1, source_start=1)
    assert f is f.original
    f.text += "d"
    assert f.text == "bcd"
    assert f is not f.original
    assert f.original.ensure_serialized() == "bc"


def test_range_equality(tmp_path: Path):
    p1 = tmp_path / "p1"
    p1.write_text("abc")

    assert TextFile(source_path=tmp_path / "p1", source_start=1) == TextFile(
        source_path=p1, source_start=1
    )
    assert TextFile(source_path=p1, source_stop=2) == TextFile(
        source_path=p1, source_stop=2
    )
    assert TextFile(source_path=p1, source_start=1, source_stop=2) == TextFile(
        source_path=p1, source_start=1, source_stop=2
    )

    assert TextFile(source_path=p1, source_start=1) != TextFile(source_path=p1)
    assert TextFile(source_path=p1, source_stop=2) != TextFile(source_path=p1)
    assert TextFile(source_path=p1, source_start=1, source_stop=2) != TextFile(
        source_path=p1, source_stop=2
    )
