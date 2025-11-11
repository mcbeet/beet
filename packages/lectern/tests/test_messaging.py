from itertools import count
from textwrap import dedent

import pytest
from beet import run_beet
from pytest_insta import SnapshotFixture

from lectern import Document

SAMPLES = [
    """
    ```
    say hello1
    ```
    """,
    """
    ```
    @function demo:foo
    say hello3
    ```
    """,
    """
    ```
    # @function demo:foo
    say hello4
    ```
    """,
    """
    `@function demo:foo`
    ```
    say hello5
    ```
    """,
    """
    ```
    say foo
    ```
    something else
    ```
    say bar
    ```
    """,
]


@pytest.mark.parametrize("message", [dedent(m).strip() for m in SAMPLES], ids=count())
def test_build(snapshot: SnapshotFixture, message: str):
    config = {
        "name": "msg",
        "pipeline": ["lectern.contrib.messaging"],
        "meta": {
            "messaging": {
                "input": message,
            }
        },
    }
    with run_beet(config) as ctx:
        document = ctx.inject(Document)
        document.markdown_serializer.flat = True
        assert snapshot("pack.md") == document
