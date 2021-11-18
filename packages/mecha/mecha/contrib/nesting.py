"""Plugin for handling nested commands."""


__all__ = [
    "AstNestedExecute",
    "NestedExecuteParser",
    "NestedCommandsTransformer",
    "parse_nested_root",
]


from dataclasses import dataclass, replace
from typing import Any, List, Set, cast

from beet import Context, ErrorMessage, Function
from beet.core.utils import required_field
from tokenstream import TokenStream, set_location

from mecha import (
    AstChildren,
    AstCommand,
    AstNode,
    AstResourceLocation,
    AstRoot,
    CompilationDatabase,
    Diagnostic,
    Mecha,
    MutatingReducer,
    Parser,
    consume_line_continuation,
    delegate,
    get_stream_scope,
    rule,
)

COMMAND_TREE = {
    "type": "root",
    "children": {
        "function": {
            "type": "literal",
            "children": {
                "name": {
                    "type": "argument",
                    "parser": "minecraft:function",
                    "executable": True,
                    "children": {
                        "commands": {
                            "type": "argument",
                            "parser": "mecha:nested_root",
                            "executable": True,
                        }
                    },
                }
            },
        },
    },
}


@dataclass(frozen=True)
class AstNestedExecute(AstNode):
    """Ast nested execute node."""

    root: AstRoot = required_field()


def beet_default(ctx: Context):
    mc = ctx.inject(Mecha)

    if not mc.spec.multiline:
        raise ErrorMessage(f"Plugin {__name__!r} requires multiline mode.")

    mc.spec.add_commands(COMMAND_TREE)

    mc.spec.parsers["nested_root"] = parse_nested_root
    mc.spec.parsers["command:argument:mecha:nested_root"] = delegate("nested_root")

    if execute := mc.spec.tree.get("execute"):
        clauses = {
            literal
            for literal, tree in execute.get_all_literals()
            if tree.redirect is None
        }

        mc.spec.parsers["command"] = NestedExecuteParser(
            parser=mc.spec.parsers["command"],
            clauses=clauses,
        )

    mc.transform.extend(NestedCommandsTransformer(ctx=ctx, database=mc.database))


def parse_nested_root(stream: TokenStream) -> AstRoot:
    """Parse nested root."""
    with stream.intercept("indent"):
        stream.expect("indent")

    level, command_level = stream.indentation[-2:]

    commands: List[AstCommand] = []

    with stream.intercept("newline"), stream.provide(
        scope=(),
        line_indentation=command_level,
    ):
        while True:
            commands.append(delegate("command", stream))

            # The command parser consumes the trailing newline so we need to rewind
            # to be able to use "consume_line_continuation()".
            while (token := stream.peek()) and not token.match("newline", "eof"):
                stream.index -= 1

            with stream.provide(multiline=True, line_indentation=level):
                if not consume_line_continuation(stream):
                    break

    node = AstRoot(commands=AstChildren(commands))
    return set_location(node, commands[0], commands[-1])


@dataclass
class NestedExecuteParser:
    """Parser for nested execute."""

    parser: Parser
    clauses: Set[str]

    def __call__(self, stream: TokenStream) -> Any:
        scope = get_stream_scope(stream)

        if scope != ("execute",):
            return self.parser(stream)

        nested = False

        with stream.checkpoint(), stream.intercept("indent"):
            stream.expect("indent")
            token = stream.get("literal")
            nested = not token or token.value not in self.clauses

        if not nested:
            return self.parser(stream)

        node = delegate("nested_root", stream)

        if len(node.commands) == 1:
            subcommand = AstCommand(
                identifier="execute:run:subcommand",
                arguments=AstChildren([node.commands[0]]),
            )
            return set_location(subcommand, node)
        else:
            return set_location(AstNestedExecute(root=node), node)


@dataclass
class NestedCommandsTransformer(MutatingReducer):
    """Transformer that handles nested commands."""

    ctx: Context = required_field()
    database: CompilationDatabase = required_field()

    def emit_function(self, path: str, root: AstRoot):
        """Helper method for emitting nested commands into a separate function."""
        function = Function()
        self.ctx.data[path] = function
        self.database[function] = replace(
            self.database[self.database.current],
            ast=root,
            resource_location=path,
        )
        self.database.enqueue(function, self.database.step + 1)

    @rule(AstCommand, identifier="function:name:commands")
    def nested_function(self, node: AstCommand):
        name, root = node.arguments

        if isinstance(name, AstResourceLocation) and isinstance(root, AstRoot):
            path = name.get_canonical_value()

            if path in self.ctx.data.functions:
                d = Diagnostic("error", f"Function {path!r} already exists.")
                raise set_location(d, name)

            self.emit_function(path, root)

        return replace(node, identifier="function:name", arguments=AstChildren([name]))

    @rule(AstNestedExecute)
    def nested_execute(self, node: AstNestedExecute):
        generate = self.ctx.generate["nested_execute"]

        if path := self.database[self.database.current].resource_location:
            path = generate.format(path + "/nested_execute_{incr}")
        else:
            path = generate.path()

        self.emit_function(path, node.root)

        resource_location = AstResourceLocation.from_value(path)

        function_call = AstCommand(
            identifier="function:name",
            arguments=AstChildren([cast(AstNode, resource_location)]),
        )
        return AstCommand(
            identifier="execute:run:subcommand",
            arguments=AstChildren([cast(AstNode, function_call)]),
        )
