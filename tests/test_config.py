import os
import json
from itertools import count
from pathlib import PurePath
from typing import Any

import pytest
from pytest_insta import SnapshotFixture

from beet import load_config
from beet.toolchain.utils import apply_option, eval_option


def encode_path(obj: Any) -> Any:
    if isinstance(obj, PurePath):
        return str(PurePath(os.path.relpath(obj)).as_posix())
    elif isinstance(obj, list):
        return [encode_path(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: encode_path(value) for key, value in obj.items()}
    else:
        return obj


@pytest.mark.parametrize("directory", sorted(os.listdir("tests/config_examples")))
def test_config_resolution(snapshot: SnapshotFixture, directory: str):
    project_config = load_config(f"tests/config_examples/{directory}/beet.json")
    d = encode_path(project_config.model_dump(warnings="none"))
    assert snapshot() == json.dumps(d, indent=2) + "\n"


@pytest.mark.parametrize(
    "overrides",
    [
        "",
        "{}",
        "a.b.c",
        '{"a":{"b":{"c":true}}}',
        "a.b.c=false",
        "foo=bar",
        "foo=123",
        "foo=3.14",
        "foo[]=bar",
        "foo = [1, 2]",
        "foo[]=1; foo[]=2",
        "foo=1; foo=[2]",
        "foo=[]",
        '{"foo":[],"thing":3}; foo.bar=hello',
        "[9]=2",
        "a=[1,2,3]; a[-1]=99; a[0]=wat",
    ],
    ids=count(),
)
def test_overrides(snapshot: SnapshotFixture, overrides: str):
    data = {}
    for override in overrides.split(";"):
        data = apply_option(data, eval_option(override))
    assert snapshot("json") == data
