"""Plugin for handling nested commands."""


__all__ = [
    "NestedCommandsTransformer",
    "NestingOptions",
    "nesting",
    "parse_nested_root",
]


from dataclasses import dataclass, replace
from importlib.resources import read_text
from typing import List, cast

from beet import Context, Function, Generator, configurable
from beet.core.utils import required_field
from jinja2 import Template
from pydantic import BaseModel
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


class NestingOptions(BaseModel):
    generate_execute: str = (
        "{% if original_location %}"
        "{{ original_location }}/"
        "{% else %}"
        "{namespace}:{path}"
        "{% endif %}"
        "nested_execute_{incr}"
    )


def beet_default(ctx: Context):
    ctx.require(nesting)


@configurable(validator=NestingOptions)
def nesting(ctx: Context, opts: NestingOptions):
    mc = ctx.inject(Mecha)

    mc.spec.multiline = True

    commands_json = read_text("mecha.resources", "nesting.json")
    mc.spec.add_commands(CommandTree.parse_raw(commands_json))

    mc.spec.parsers["nested_root"] = parse_nested_root
    mc.spec.parsers["command:argument:mecha:nested_root"] = delegate("nested_root")

    mc.transform.extend(
        NestedCommandsTransformer(
            generate=ctx.generate,
            database=mc.database,
            generate_execute_template=ctx.template.compile(opts.generate_execute),
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
class NestedCommandsTransformer(MutatingReducer):
    """Transformer that handles nested commands."""

    generate: Generator = required_field()
    database: CompilationDatabase = required_field()
    generate_execute_template: Template = required_field()

    def emit_function(self, path: str, root: AstRoot):
        """Helper method for emitting nested commands into a separate function."""
        function = Function()
        self.generate(path, function)
        self.database[function] = replace(
            self.database[self.database.current],
            ast=root,
            resource_location=path,
        )
        self.database.enqueue(function, self.database.step + 1)

    @rule(AstCommand, identifier="execute:subcommand")
    def nesting_execute_run(self, node: AstCommand):
        if isinstance(command := node.arguments[0], AstCommand):
            if command.identifier == "execute:run:subcommand":
                return command.arguments[0]
        return node

    @rule(AstCommand, identifier="execute:run:subcommand")
    def nesting_execute_function(self, node: AstCommand):
        if isinstance(command := node.arguments[0], AstCommand):
            if command.identifier in [
                "function:name:commands",
                "append:function:name:commands",
                "prepend:function:name:commands",
            ]:
                self.handle_function(command)
                command = replace(
                    command,
                    identifier="function:name",
                    arguments=AstChildren([command.arguments[0]]),
                )
                return replace(node, arguments=AstChildren([command]))

        return node

    @rule(AstCommand, identifier="execute:commands")
    def nesting_execute_commands(self, node: AstCommand):
        root = cast(AstRoot, node.arguments[0])

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

            if subcommand.identifier == "execute:subcommand":
                return subcommand.arguments[0]

        else:
            original_location = self.database[self.database.current].resource_location
            path = self.generate.format(
                self.generate_execute_template.render(
                    original_location=original_location
                )
            )

            self.emit_function(path, root)

            subcommand = AstCommand(
                identifier="function:name",
                arguments=AstChildren([AstResourceLocation.from_value(path)]),
            )

        return AstCommand(
            identifier="execute:run:subcommand",
            arguments=AstChildren([subcommand]),
        )

    @rule(AstCommand, identifier="schedule:function:function:time:commands")
    @rule(AstCommand, identifier="schedule:function:function:time:append:commands")
    @rule(AstCommand, identifier="schedule:function:function:time:replace:commands")
    def nesting_schedule_function(self, node: AstCommand):
        self.handle_function(
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
            if command.identifier in [
                "function:name:commands",
                "append:function:name:commands",
                "prepend:function:name:commands",
            ]:
                commands.extend(self.handle_function(command, top_level=True))
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
    ) -> List[AstCommand]:
        name, root = node.arguments

        if isinstance(name, AstResourceLocation) and isinstance(root, AstRoot):
            path = name.get_canonical_value()

            if not top_level:
                if node.identifier == "append:function:name:commands":
                    d = Diagnostic("error", f"Can't append commands with execute.")
                    raise set_location(d, node, name)
                if node.identifier == "prepend:function:name:commands":
                    d = Diagnostic("error", f"Can't prepend commands with execute.")
                    raise set_location(d, node, name)

            target = self.database.index.get(path)

            if not target:
                self.emit_function(path, root)

            elif node.identifier == "function:name:commands":
                if self.database[target].ast != root:
                    d = Diagnostic(
                        "error",
                        f'Redefinition of function "{path}" doesn\'t match existing implementation.',
                    )
                    raise set_location(d, name)

            elif target is self.database.current:
                if node.identifier == "prepend:function:name:commands":
                    d = Diagnostic(
                        "error",
                        f'Can\'t prepend commands to the current function "{path}".',
                    )
                    raise set_location(d, node, name)

                return list(root.commands)

            else:
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

        else:
            return [node]
