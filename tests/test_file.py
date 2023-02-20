import json
from pathlib import Path
from typing import Any, List, Literal, Union

import pytest
from pydantic import BaseModel, Field
from typing_extensions import Annotated

from beet import BinaryFile, JsonFileBase, TextFile


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
    f = TextFile[Any](source_path=p1, source_start=1)
    assert f is f.original
    f.text += "d"
    assert f.text == "bcd"
    assert f is not f.original
    assert f.original is f.original.original
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


class A(BaseModel):
    type: Literal["a"]
    a: int


class B(BaseModel):
    type: Literal["b"]
    b: str


class AB(BaseModel):
    __root__: Annotated[Union[A, B], Field(discriminator="type")]


class ABGroup(BaseModel):
    __root__: Union[AB, List[AB]]


class ABFile(JsonFileBase[Any, ABGroup]):

    model = ABGroup


@pytest.mark.parametrize(
    "data",
    [
        '{"type": "a", "a": 42}',
        '{"type": "b", "b": "foo"}',
        '[{"type": "a", "a": 42}, {"type": "b", "b": "foo"}]',
    ],
)
def test_model(data: str):
    ab = ABFile(data)
    ab.ensure_deserialized()
    assert json.loads(data) == json.loads(ab.text)


def test_copy():
    assert TextFile(source_path="foo.txt").copy().source_path == "foo.txt"
    assert TextFile("hello").copy().text == "hello"
