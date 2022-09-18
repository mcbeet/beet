"""Plugin for handling nested resources."""


__all__ = [
    "NestedResourcesTransformer",
]


from dataclasses import dataclass, replace
from typing import Dict, List, Type

from beet import Context, DataModelBase, Generator, NamespaceFile, TagFile
from beet.core.utils import required_field, snake_case
from tokenstream import set_location

from mecha import (
    AstChildren,
    AstCommand,
    AstJson,
    AstResourceLocation,
    AstRoot,
    CompilationDatabase,
    Diagnostic,
    Mecha,
    MultilineParser,
    MutatingReducer,
    delegate,
    rule,
)

NESTED_JSON_COMMAND_TREE = {
    "type": "literal",
    "children": {
        "name": {
            "type": "argument",
            "parser": "minecraft:resource_location",
            "children": {
                "content": {
                    "type": "argument",
                    "parser": "mecha:nested_json",
                    "executable": True,
                }
            },
        }
    },
}


def beet_default(ctx: Context):
    ctx.require("mecha.contrib.nesting")

    mc = ctx.inject(Mecha)

    json_resources = {
        snake_case(file_type.__name__): file_type
        for pack in ctx.packs
        for file_type in pack.resolve_scope_map().values()
        if issubclass(file_type, DataModelBase)
    }

    # Make sure there's no confusion between nested resources and existing commands.
    for name, tree in mc.spec.tree.get_all_literals():
        if name in json_resources and any(tree.get_all_arguments()):
            json_resources[f"{name}_file"] = json_resources.pop(name)

    commands = {name: NESTED_JSON_COMMAND_TREE for name in json_resources}
    tag_commands = {
        name: NESTED_JSON_COMMAND_TREE
        for name, file_type in json_resources.items()
        if issubclass(file_type, TagFile)
    }

    mc.spec.add_commands(
        {
            "type": "root",
            "children": {
                **commands,
                "merge": {"type": "literal", "children": commands},
                "append": {"type": "literal", "children": tag_commands},
                "prepend": {"type": "literal", "children": tag_commands},
            },
        }
    )

    mc.spec.parsers["nested_json"] = delegate("json")
    mc.spec.parsers["command:argument:mecha:nested_json"] = MultilineParser(
        delegate("nested_json")
    )

    mc.transform.extend(
        NestedResourcesTransformer(
            generate=ctx.generate,
            database=mc.database,
            json_identifiers={
                f"{prefix}{name}:name:content": file_type
                for name, file_type in json_resources.items()
                for prefix in ["", "merge:"]
                + ["append:", "prepend:"] * issubclass(file_type, TagFile)
            },
        )
    )


@dataclass
class NestedResourcesTransformer(MutatingReducer):
    """Transformer that handles nested resources."""

    generate: Generator = required_field()
    database: CompilationDatabase = required_field()

    json_identifiers: Dict[str, Type[NamespaceFile]] = required_field()

    @rule(AstRoot)
    def nested_resources(self, node: AstRoot):
        changed = False
        commands: List[AstCommand] = []

        for command in node.commands:
            if file_type := self.json_identifiers.get(command.identifier):
                name, content = command.arguments

                if isinstance(name, AstResourceLocation) and isinstance(
                    content, AstJson
                ):
                    full_name = name.get_canonical_value()
                    file_instance = file_type(
                        content.evaluate(),
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
            and subcommand.identifier in self.json_identifiers
        ):
            d = Diagnostic("error", "Nested resource not allowed behind execute.")
            raise set_location(d, subcommand, subcommand.arguments[0])
        return node
