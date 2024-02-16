"""Plugin for handling nested resources."""

__all__ = [
    "NestedResources",
    "NestedResourcesTransformer",
    "AstNestedText",
    "parse_nested_text",
]


from dataclasses import dataclass, replace
from textwrap import dedent
from typing import Any, Dict, List, Type, Union, cast

from beet import (
    Context,
    DataModelBase,
    DataPack,
    Generator,
    JsonFileBase,
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
from mecha.contrib.json_files import (
    AstAppendJsonContent,
    AstJsonContent,
    AstMergeJsonContent,
    AstPrependJsonContent,
    JsonFileCompilation,
)


def beet_default(ctx: Context):
    ctx.require("mecha.contrib.nesting")
    ctx.inject(NestedResources).prepare(ctx.generate, ctx.inject(JsonFileCompilation))


class NestedResources:
    mc: Mecha
    text_resources: Dict[str, Type[NamespaceFile]]
    json_resources: Dict[str, Type[NamespaceFile]]

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

        should_disambiguate = {
            name
            for name, tree in self.mc.spec.tree.get_all_literals()
            if any(tree.get_all_arguments())
        }

        self.text_resources = {
            (
                f"{file_type.snake_name}_file"
                if file_type.snake_name in should_disambiguate
                else file_type.snake_name
            ): file_type
            for pack in packs
            for file_type in pack.get_file_types(extend=TextFileBase)
        }

        self.json_resources = {
            name: self.text_resources.pop(name)
            for name, file_type in list(self.text_resources.items())
            if issubclass(file_type, DataModelBase)
        }

    def prepare(self, generate: Generator, json_file_compilation: JsonFileCompilation):
        text_commands = {
            name: self.create_command_tree_fragment("mecha:nested_text")
            for name in self.text_resources
        }

        json_commands = {
            name: self.create_command_tree_fragment("mecha:nested_json")
            for name in self.json_resources
        }

        tag_commands = {
            name: self.create_command_tree_fragment("mecha:nested_json")
            for name, file_type in self.json_resources.items()
            if issubclass(file_type, TagFile)
        }

        self.mc.spec.add_commands(
            {
                "type": "root",
                "children": {
                    **text_commands,
                    **json_commands,
                    "merge": {"type": "literal", "children": json_commands},
                    "append": {"type": "literal", "children": tag_commands},
                    "prepend": {"type": "literal", "children": tag_commands},
                },
            }
        )

        self.mc.spec.parsers["nested_text"] = parse_nested_text
        self.mc.spec.parsers["command:argument:mecha:nested_text"] = MultilineParser(
            delegate("nested_text")
        )

        self.mc.spec.parsers["nested_json"] = delegate("json")
        self.mc.spec.parsers["command:argument:mecha:nested_json"] = MultilineParser(
            delegate("nested_json")
        )

        self.mc.transform.extend(
            NestedResourcesTransformer(
                generate=generate,
                database=self.mc.database,
                nested_resource_identifiers={
                    f"{prefix}{name}:name:content": file_type
                    for name, file_type in self.text_resources.items()
                    | self.json_resources.items()
                    for prefix in [""]
                    + ["merge:"] * issubclass(file_type, DataModelBase)
                    + ["append:", "prepend:"] * issubclass(file_type, TagFile)
                },
                json_file_compilation=json_file_compilation,
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
    json_file_compilation: JsonFileCompilation = required_field()

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

                    if isinstance(content, AstJson) and (
                        cast(Type[JsonFileBase[Any]], file_type)
                        in self.json_file_compilation.file_types
                    ):
                        if command.identifier.startswith("merge:"):
                            content_type = AstMergeJsonContent
                        elif command.identifier.startswith("append:"):
                            content_type = AstAppendJsonContent
                        elif command.identifier.startswith("prepend:"):
                            content_type = AstPrependJsonContent
                        else:
                            content_type = AstJsonContent

                        root = content_type.create_root_node(content)

                        file_instance = file_type(
                            original=self.database.current.original
                        )
                        target = cast(
                            JsonFileBase[Any],
                            self.generate(full_name, default=file_instance),
                        )

                        compilation_unit = self.database.get(target)
                        if not compilation_unit:
                            compilation_unit = replace(
                                self.database[self.database.current],
                                ast=(
                                    root
                                    if target is file_instance
                                    else AstJsonContent.create_root_node(
                                        AstJson.from_value(target.data)
                                    )
                                ),
                                resource_location=full_name,
                                no_index=True,
                            )
                            self.database[target] = compilation_unit
                            self.database.enqueue(target, self.database.step + 1)

                        if compilation_unit.ast:
                            if content_type is AstJsonContent:
                                for command in compilation_unit.ast.commands:
                                    if isinstance(command, AstJsonContent):
                                        if command != root.commands[0]:
                                            d = Diagnostic(
                                                level="error",
                                                message=f'Redefinition of {snake_case(file_type.__name__)} "{full_name}" doesn\'t match existing file.',
                                            )
                                            yield set_location(d, name)
                                        break
                            else:
                                compilation_unit.ast = replace(
                                    compilation_unit.ast,
                                    commands=AstChildren(
                                        compilation_unit.ast.commands + root.commands
                                    ),
                                )
                        else:
                            compilation_unit.ast = root

                        changed = True
                        continue

                    file_instance = file_type(
                        (
                            content.evaluate()
                            if isinstance(content, AstJson)
                            else content.value
                        ),
                        original=self.database.current.original,
                    )

                    target = self.generate(full_name, default=file_instance)
                    if target is not file_instance:
                        if command.identifier.startswith("merge:"):
                            if not target.merge(file_instance):
                                target.set_content(file_instance.get_content())
                        elif command.identifier.startswith("append:"):
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
