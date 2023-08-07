"""Plugin for handling nested resources."""


__all__ = [
    "NestedResources",
    "NestedResourcesTransformer",
    "AstNestedText",
    "parse_nested_text",
]


from dataclasses import dataclass, replace
from textwrap import dedent
from typing import Dict, List, Type, Union

from beet import (
    Context,
    DataModelBase,
    DataPack,
    Generator,
    NamespaceFile,
    ResourcePack,
    TagFile,
    TextFileBase,
)
from beet.core.utils import JsonDict, required_field, snake_case
from tokenstream import InvalidSyntax, Token, TokenStream, set_location

from mecha import (
    AstChildren,
    AstCommand,
    AstJson,
    AstNode,
    AstResourceLocation,
    AstRoot,
    CompilationDatabase,
    Diagnostic,
    Mecha,
    MultilineParser,
    MutatingReducer,
    consume_line_continuation,
    delegate,
    rule,
)


def beet_default(ctx: Context):
    ctx.require("mecha.contrib.nesting")
    ctx.inject(NestedResources).prepare(ctx.generate)


class NestedResources:
    mc: Mecha
    json_resources: Dict[str, Type[NamespaceFile]]
    text_resources: Dict[str, Type[NamespaceFile]]

    def __init__(
        self,
        arg: Union[Mecha, Context],
        *packs: Union[ResourcePack, DataPack],
    ):
        if isinstance(arg, Context):
            packs += arg.packs
            self.mc = arg.inject(Mecha)
        else:
            self.mc = arg

        nested_resources = {
            snake_case(file_type.__name__): file_type
            for pack in packs
            for file_type in pack.resolve_scope_map().values()
        }

        # Make sure there's no confusion between nested resources and existing commands.
        for name, tree in self.mc.spec.tree.get_all_literals():
            if name in nested_resources and any(tree.get_all_arguments()):
                nested_resources[f"{name}_file"] = nested_resources.pop(name)

        self.json_resources = {
            name: file_type
            for name, file_type in nested_resources.items()
            if issubclass(file_type, DataModelBase)
        }

        for name in self.json_resources:
            del nested_resources[name]

        self.text_resources = {
            name: file_type
            for name, file_type in nested_resources.items()
            if issubclass(file_type, TextFileBase)
        }

    def prepare(self, generate: Generator):
        json_commands = {
            name: self.create_command_tree_fragment("mecha:nested_json")
            for name in self.json_resources
        }

        tag_commands = {
            name: self.create_command_tree_fragment("mecha:nested_json")
            for name, file_type in self.json_resources.items()
            if issubclass(file_type, TagFile)
        }

        text_commands = {
            name: self.create_command_tree_fragment("mecha:nested_text")
            for name in self.text_resources
        }

        self.mc.spec.add_commands(
            {
                "type": "root",
                "children": {
                    **json_commands,
                    "merge": {"type": "literal", "children": json_commands},
                    "append": {"type": "literal", "children": tag_commands},
                    "prepend": {"type": "literal", "children": tag_commands},
                    **text_commands,
                },
            }
        )

        self.mc.spec.parsers["nested_json"] = delegate("json")
        self.mc.spec.parsers["command:argument:mecha:nested_json"] = MultilineParser(
            delegate("nested_json")
        )

        self.mc.spec.parsers["nested_text"] = parse_nested_text
        self.mc.spec.parsers["command:argument:mecha:nested_text"] = MultilineParser(
            delegate("nested_text")
        )

        self.mc.transform.extend(
            NestedResourcesTransformer(
                generate=generate,
                database=self.mc.database,
                nested_resource_identifiers={
                    f"{prefix}{name}:name:content": file_type
                    for name, file_type in self.json_resources.items()
                    | self.text_resources.items()
                    for prefix in [""]
                    + ["merge:"] * issubclass(file_type, DataModelBase)
                    + ["append:", "prepend:"] * issubclass(file_type, TagFile)
                },
            )
        )

    @staticmethod
    def create_command_tree_fragment(parser: str) -> JsonDict:
        return {
            "type": "literal",
            "children": {
                "name": {
                    "type": "argument",
                    "parser": "minecraft:resource_location",
                    "children": {
                        "content": {
                            "type": "argument",
                            "parser": parser,
                            "executable": True,
                        }
                    },
                }
            },
        }


@dataclass(frozen=True, slots=True)
class AstNestedText(AstNode):
    """Ast nested text node."""

    value: str = required_field()


def parse_nested_text(stream: TokenStream) -> AstNestedText:
    with stream.syntax(colon=r":"):
        colon = stream.expect("colon")

    with stream.intercept("newline"), stream.syntax(text=r"[^\s].*", comment=None):
        if not consume_line_continuation(stream):
            exc = InvalidSyntax("Expected non-empty block.")
            raise set_location(exc, colon)

        start_pos = stream.current.location.pos
        level = stream.indentation[-2]

        lines: List[Token] = []

        while True:
            lines.append(stream.expect("text"))

            with stream.provide(multiline=True, line_indentation=level):
                if not consume_line_continuation(stream):
                    break

    node = AstNestedText(
        value=dedent(stream.source[start_pos : lines[-1].end_location.pos] + "\n")
    )
    return set_location(node, lines[0], lines[-1])


@dataclass
class NestedResourcesTransformer(MutatingReducer):
    """Transformer that handles nested resources."""

    generate: Generator = required_field()
    database: CompilationDatabase = required_field()

    nested_resource_identifiers: Dict[str, Type[NamespaceFile]] = required_field()

    @rule(AstRoot)
    def nested_resources(self, node: AstRoot):
        changed = False
        commands: List[AstCommand] = []

        for command in node.commands:
            if file_type := self.nested_resource_identifiers.get(command.identifier):
                name, content = command.arguments

                if isinstance(name, AstResourceLocation) and isinstance(
                    content, (AstJson, AstNestedText)
                ):
                    full_name = name.get_canonical_value()
                    file_instance = file_type(
                        content.evaluate()
                        if isinstance(content, AstJson)
                        else content.value,
                        original=self.database.current.original,
                    )

                    if command.identifier.startswith("merge:"):
                        self.generate(full_name, merge=file_instance)
                        changed = True
                        continue

                    target = self.generate(full_name, default=file_instance)
                    if target is not file_instance:
                        if command.identifier.startswith("append:"):
                            target.append(file_instance)  # type: ignore
                        elif command.identifier.startswith("prepend:"):
                            target.prepend(file_instance)  # type: ignore
                        elif (
                            target.ensure_deserialized()
                            != file_instance.ensure_deserialized()
                        ):
                            d = Diagnostic(
                                level="error",
                                message=f'Redefinition of {snake_case(file_type.__name__)} "{full_name}" doesn\'t match existing file.',
                            )
                            yield set_location(d, name)

                    changed = True
                    continue

            commands.append(command)

        if changed:
            return replace(node, commands=AstChildren(commands))

        return node

    @rule(AstCommand, identifier="execute:run:subcommand")
    def execute_nested_resource(self, node: AstCommand):
        if (
            isinstance(subcommand := node.arguments[0], AstCommand)
            and subcommand.identifier in self.nested_resource_identifiers
        ):
            d = Diagnostic("error", "Nested resource not allowed behind execute.")
            yield set_location(d, subcommand, subcommand.arguments[0])
        return node
