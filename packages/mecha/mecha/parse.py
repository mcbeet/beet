__all__ = [
    "get_default_parsers",
    "delegate",
    "parse_root",
    "parse_command",
    "parse_argument",
    "parse_brigadier_bool",
]


from typing import TYPE_CHECKING, Any, Dict, List, Tuple

from tokenstream import SourceLocation, TokenStream

from .ast import AstChildren, AstCommand, AstNode, AstRoot, AstValue
from .spec import CommandSpecification, Parser


def get_default_parsers() -> Dict[str, Parser]:
    """Return the default parsers."""
    return {
        "root": parse_root,
        "command": parse_command,
        "argument": parse_argument,
        "brigadier:bool": parse_brigadier_bool,
    }


def delegate(stream: TokenStream, parser: str) -> Any:
    """Delegate parsing to a registered subparser."""
    spec: CommandSpecification = stream.data["spec"]

    if parser not in spec.parsers:
        raise ValueError(f"Unrecognized parser {parser!r}.")

    return spec.parsers[parser](stream)


def parse_root(stream: TokenStream) -> AstRoot:
    """Parse root."""
    with stream.syntax(comment=r"#.+$", literal=r"\S+"), stream.intercept("newline"):
        start = stream.peek()

        if not start:
            return AstRoot(
                filename=None,
                commands=AstChildren(),
                location=SourceLocation(0, 1, 1),
                end_location=SourceLocation(0, 1, 1),
            )

        commands: List[AstCommand] = []

        for _ in stream.peek_until():
            while stream.get("newline", "comment"):
                continue
            if stream.peek():
                commands.append(delegate(stream, "command"))

        return AstRoot(
            filename=None,
            commands=AstChildren(commands),
            location=start.location,
            end_location=stream.current.end_location,
        )


def parse_command(stream: TokenStream) -> AstCommand:
    """Parse command."""
    spec: CommandSpecification = stream.data["spec"]

    arguments: List[AstNode] = []
    scope: Tuple[str, ...] = ()

    with stream.checkpoint():
        location = stream.expect().location
        end_location = location

    while (tree := spec.flattened_tree[scope]) and not (
        tree.executable and stream.get("newline")
    ):
        literal_names = list(tree.get_literal_children())
        argument_names = list(tree.get_argument_children())

        with stream.alternative(bool(argument_names)):
            patterns = [("literal", name) for name in literal_names]
            token = stream.expect_any(*patterns)
            scope += (token.value,)
            if not TYPE_CHECKING:
                continue

        for name, alternative in stream.choose(*argument_names):
            with alternative, stream.provide(scope=scope + (name,)):
                arguments.append(delegate(stream, "argument"))
                scope += (name,)

        end_location = stream.current.end_location

    return AstCommand(
        identifier=":".join(scope),
        arguments=AstChildren(arguments),
        location=location,
        end_location=end_location,
    )


def parse_argument(stream: TokenStream) -> AstNode:
    """Parse argument."""
    spec: CommandSpecification = stream.data["spec"]
    tree = spec.flattened_tree[stream.data["scope"]]

    if tree.parser:
        return delegate(stream, tree.parser)

    raise ValueError(f"Missing argument parser in command tree {stream.data['scope']}.")


def parse_brigadier_bool(stream: TokenStream) -> AstValue[bool]:
    """Parse brigadier bool."""
    token = stream.expect_any(("literal", "true"), ("literal", "false"))

    return AstValue[bool](
        value=token.value == "true",
        location=token.location,
        end_location=token.end_location,
    )
