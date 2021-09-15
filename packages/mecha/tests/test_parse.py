import pytest
from beet.core.utils import JsonDict
from pytest_insta import SnapshotFixture
from tokenstream import InvalidSyntax, TokenStream

from mecha import Mecha, delegate, get_argument_examples, get_command_examples


def test_command_examples(snapshot: SnapshotFixture, mc: Mecha):
    ast = mc.parse_function(get_command_examples())
    assert snapshot() == ast.dump()
    assert snapshot() == mc.serialize(ast)


@pytest.mark.parametrize(
    "test_name, properties, invalid, value",
    params := [
        (
            f"{argument_parser} {i} {j}",
            suite.get("properties", {}),
            suite.get("invalid", False),
            value,
        )
        for argument_parser, suites in get_argument_examples().items()
        for i, suite in enumerate(suites)
        for j, value in enumerate(suite["examples"])
    ],
    ids=[args[0] for args in params],
)
def test_argument_examples(
    snapshot: SnapshotFixture,
    mc: Mecha,
    test_name: str,
    properties: JsonDict,
    invalid: bool,
    value: str,
):
    argument_parser = f"command:argument:{test_name.partition(' ')[0]}"
    if argument_parser not in mc.spec.parsers:
        pytest.skip()

    stream = TokenStream(value)

    with mc.prepare_token_stream(stream), stream.provide(properties=properties):
        if invalid:
            with pytest.raises(InvalidSyntax) as exc_info:
                delegate(argument_parser, stream)
            assert snapshot() == "\n---\n".join(
                [
                    test_name,
                    str(properties),
                    value,
                    f"{exc_info.type.__name__}: {exc_info.value}\n\nlocation = {exc_info.value.location}\nend_location = {exc_info.value.end_location}",
                ]
            )
        else:
            ast = delegate(argument_parser, stream)
            assert snapshot() == "\n---\n".join(
                [test_name, str(properties), value, mc.serialize(ast), ast.dump()]
            )
