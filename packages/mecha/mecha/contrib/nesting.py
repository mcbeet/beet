"""Plugin for handling nested commands."""

__all__ = [
    "NestedCommandsTransformer",
    "NestingOptions",
    "nesting",
    "parse_nested_root",
]


from dataclasses import dataclass, field, replace
from importlib.resources import files
from typing import Generator, List, cast

from beet import Context, Function
from beet import Generator as BeetGenerator
from beet import configurable
from beet.core.utils import required_field
from pydantic.v1 import BaseModel
from tokenstream import InvalidSyntax, TokenStream, set_location

from mecha import (
    AstChildren,
    AstCommand,
    AstResourceLocation,
    AstRoot,
    CommandTree,
    CompilationDatabase,
    Diagnostic,
    Mecha,
    MutatingReducer,
    consume_line_continuation,
    delegate,
    rule,
)
from mecha.contrib.nested_location import NestedLocationResolver


class NestingOptions(BaseModel):
    generate_execute: str = "nested_execute_{incr}"
    generate_macro: str = "nested_macro_{incr}"
    generate_return: str = "nested_return_{incr}"


def beet_default(ctx: Context):
    ctx.require(nesting)


@configurable(validator=NestingOptions)
def nesting(ctx: Context, opts: NestingOptions):
    mc = ctx.inject(Mecha)

    mc.spec.multiline = True

    commands_json = files("mecha.resources").joinpath("nesting.json").read_text()
    mc.spec.add_commands(CommandTree.parse_raw(commands_json))

    mc.spec.parsers["nested_root"] = parse_nested_root
    mc.spec.parsers["command:argument:mecha:nested_root"] = delegate("nested_root")

    mc.transform.extend(
        NestedCommandsTransformer(
            generate=ctx.generate,
            database=mc.database,
            generate_execute_template=opts.generate_execute,
            generate_macro_template=opts.generate_macro,
            generate_return_template=opts.generate_return,
            nested_location_resolver=ctx.inject(NestedLocationResolver),
        )
    )


def parse_nested_root(stream: TokenStream) -> AstRoot:
    """Parse nested root."""
    with stream.syntax(colon=r":"):
        colon = stream.expect("colon")

    if not consume_line_continuation(stream):
        exc = InvalidSyntax("Expected non-empty block.")
        raise set_location(exc, colon)

    level, command_level = stream.indentation[-2:]

    commands: List[AstCommand] = []

    with (
        stream.intercept("newline"),
        stream.provide(
            scope=(),
            line_indentation=command_level,
        ),
    ):
        while True:
            commands.append(delegate("root_item", stream))

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
class NestedCommandsTransformer(MutatingReducer):
    """Transformer that handles nested commands."""

    generate: BeetGenerator = required_field()
    database: CompilationDatabase = required_field()
    generate_execute_template: str = required_field()
    generate_macro_template: str = required_field()
    generate_return_template: str = required_field()
    nested_location_resolver: NestedLocationResolver = required_field()

    identifier_map: dict[str, str] = field(
        default_factory=lambda: {
            "function:name:commands": "function:name",
            "function:name:arguments:commands": "function:name:arguments",
            "function:name:with:block:sourcePos:commands": "function:name:with:block:sourcePos",
            "function:name:with:block:sourcePos:path:commands": "function:name:with:block:sourcePos:path",
            "function:name:with:entity:source:commands": "function:name:with:entity:source",
            "function:name:with:entity:source:path:commands": "function:name:with:entity:source:path",
            "function:name:with:storage:source:commands": "function:name:with:storage:source",
            "function:name:with:storage:source:path:commands": "function:name:with:storage:source:path",
            "append:function:name:commands": "function:name",
            "prepend:function:name:commands": "function:name",
        }
    )

    def emit_function(self, path: str, root: AstRoot):
        """Helper method for emitting nested commands into a separate function."""
        function = Function(original=self.database.current.original)
        self.generate(path, function)
        self.database[function] = replace(
            self.database[self.database.current],
            ast=root,
            resource_location=path,
        )
        self.database.enqueue(function, self.database.step + 1)

    @rule(AstCommand, identifier="execute:subcommand")
    def nesting_execute_run(self, node: AstCommand):
        if node.arguments and isinstance(command := node.arguments[0], AstCommand):
            if command.identifier == "execute:run:subcommand":
                return command.arguments[0]
        return node

    @rule(AstCommand, identifier="execute:run:subcommand")
    @rule(AstCommand, identifier="return:run:subcommand")
    def nesting_run_function(self, node: AstCommand):
        if isinstance(command := node.arguments[0], AstCommand):
            if command.identifier in self.identifier_map:
                yield from self.handle_function(command)
                command = replace(
                    command,
                    identifier=self.identifier_map[command.identifier],
                    arguments=AstChildren(command.arguments[:-1]),
                )
                return replace(node, arguments=AstChildren([command]))

        return node

    @rule(AstCommand, identifier="execute:commands")
    @rule(AstCommand, identifier="return:commands")
    def nesting_execute_commands(self, node: AstCommand):
        root = cast(AstRoot, node.arguments[0])

        if node.identifier == "execute:commands":
            generate_template = self.generate_execute_template
            identifier = "execute:run:subcommand"
        else:
            generate_template = self.generate_return_template
            identifier = "return:run:subcommand"

        single_command = None
        for command in root.commands:
            if command.compile_hints.get("skip_execute_inline_single_command"):
                continue
            if single_command is None:
                single_command = command
            else:
                single_command = None
                break

        if single_command:
            subcommand = single_command

            if (
                node.identifier == "execute:commands"
                and subcommand.identifier == "execute:subcommand"
            ):
                return subcommand.arguments[0]

        else:
            namespace, resolved = self.nested_location_resolver.resolve()
            path = self.generate.format(f"{namespace}:{resolved}/{generate_template}")

            self.emit_function(path, root)

            subcommand = AstCommand(
                identifier="function:name",
                arguments=AstChildren([AstResourceLocation.from_value(path)]),
            )

        return AstCommand(
            identifier=identifier,
            arguments=AstChildren([subcommand]),
        )

    @rule(AstCommand, identifier="with:block:sourcePos:commands")
    @rule(AstCommand, identifier="with:block:sourcePos")
    @rule(AstCommand, identifier="with:block:sourcePos:path:commands")
    @rule(AstCommand, identifier="with:block:sourcePos:path")
    @rule(AstCommand, identifier="with:entity:source:commands")
    @rule(AstCommand, identifier="with:entity:source")
    @rule(AstCommand, identifier="with:entity:source:path:commands")
    @rule(AstCommand, identifier="with:entity:source:path")
    @rule(AstCommand, identifier="with:storage:source:commands")
    @rule(AstCommand, identifier="with:storage:source")
    @rule(AstCommand, identifier="with:storage:source:path:commands")
    @rule(AstCommand, identifier="with:storage:source:path")
    def nesting_macro_commands(self, node: AstCommand):
        identifier = node.identifier.split(":")
        if not identifier[-1] == "commands":
            d = Diagnostic(
                "error", "Anonymous macro invocation requires nested commands."
            )
            return set_location(d, node)

        if isinstance(root := node.arguments[-1], AstRoot):
            namespace, resolved = self.nested_location_resolver.resolve()
            path = self.generate.format(
                f"{namespace}:{resolved}/{self.generate_macro_template}"
            )

            self.emit_function(path, root)

            command = AstCommand(
                identifier=":".join(["function", "name"] + identifier[:-1]),
                arguments=AstChildren(
                    [AstResourceLocation.from_value(path), *node.arguments[:-1]]
                ),
            )
            return set_location(command, node)

        return node

    @rule(AstCommand, identifier="schedule:function:function:time:commands")
    @rule(AstCommand, identifier="schedule:function:function:time:append:commands")
    @rule(AstCommand, identifier="schedule:function:function:time:replace:commands")
    def nesting_schedule_function(self, node: AstCommand):
        yield from self.handle_function(
            AstCommand(
                identifier="function:name:commands",
                arguments=AstChildren([node.arguments[0], node.arguments[-1]]),
            )
        )

        return replace(
            node,
            identifier=node.identifier[:-9],
            arguments=AstChildren(node.arguments[:-1]),
        )

    @rule(AstRoot)
    def nesting(self, node: AstRoot):
        changed = False
        commands: List[AstCommand] = []

        for command in node.commands:
            if command.identifier in self.identifier_map:
                result = yield from self.handle_function(command, top_level=True)
                commands.extend(result)
                changed = True
                continue

            args = command.arguments
            stack: List[AstCommand] = [command]

            expand = None

            while args and isinstance(subcommand := args[-1], AstCommand):
                if subcommand.identifier == "execute:expand:commands":
                    expand = subcommand
                    break
                stack.append(subcommand)
                args = subcommand.arguments

            if expand:
                changed = True
                for nested_command in cast(AstRoot, expand.arguments[0]).commands:
                    if nested_command.identifier == "execute:subcommand":
                        expansion = cast(AstCommand, nested_command.arguments[0])
                    else:
                        expansion = AstCommand(
                            identifier="execute:run:subcommand",
                            arguments=AstChildren([nested_command]),
                        )
                        expansion = set_location(expansion, nested_command)

                    for prefix in reversed(stack):
                        args = AstChildren([*prefix.arguments[:-1], expansion])
                        expansion = replace(prefix, arguments=args)

                    commands.append(expansion)

            else:
                commands.append(command)

        if changed:
            return replace(node, commands=AstChildren(commands))

        return node

    def handle_function(
        self,
        node: AstCommand,
        top_level: bool = False,
    ) -> Generator[Diagnostic, None, List[AstCommand]]:
        name, *args, root = node.arguments

        if isinstance(name, AstResourceLocation) and isinstance(root, AstRoot):
            path = name.get_canonical_value()

            if top_level:
                if node.identifier in (
                    "function:name:arguments:commands",
                    "function:name:with:block:sourcePos:commands",
                    "function:name:with:block:sourcePos:path:commands",
                    "function:name:with:entity:source:commands",
                    "function:name:with:entity:source:path:commands",
                    "function:name:with:storage:source:commands",
                    "function:name:with:storage:source:path:commands",
                ):
                    d = Diagnostic(
                        "error",
                        f"Nested function definition can not include arguments.",
                    )
                    d.notes.append(
                        'Prefix with "execute" to invoke the nested function.'
                    )
                    yield set_location(d, node, args[-1])
                    return []
            else:
                if node.identifier == "append:function:name:commands":
                    d = Diagnostic("error", f"Can't append commands with execute.")
                    yield set_location(d, node, name)
                    return []
                if node.identifier == "prepend:function:name:commands":
                    d = Diagnostic("error", f"Can't prepend commands with execute.")
                    yield set_location(d, node, name)
                    return []

            target = self.database.index.get(path)

            if node.identifier in (
                "append:function:name:commands",
                "prepend:function:name:commands",
            ):
                if ":".join(self.nested_location_resolver.resolve()) == path:
                    if node.identifier == "prepend:function:name:commands":
                        d = Diagnostic(
                            "error",
                            f'Can\'t prepend commands to the current function "{path}".',
                        )
                        yield set_location(d, node, name)
                        return []
                    return list(root.commands)

                if not target:
                    self.emit_function(path, root)
                    return []

                compilation_unit = self.database[target]

                if compilation_unit.ast:
                    compilation_unit.ast = replace(
                        compilation_unit.ast,
                        commands=AstChildren(
                            compilation_unit.ast.commands + root.commands
                            if node.identifier == "append:function:name:commands"
                            else root.commands + compilation_unit.ast.commands
                        ),
                    )
                else:
                    compilation_unit.ast = root

                return []

            elif not target:
                self.emit_function(path, root)
                return []

            elif self.database[target].ast != root:
                d = Diagnostic(
                    "error",
                    f'Redefinition of function "{path}" doesn\'t match existing implementation.',
                )
                yield set_location(d, name)
                return []

            else:
                return []

        else:
            return [node]
