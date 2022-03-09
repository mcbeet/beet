"""Plugin for handling nested resources."""


__all__ = [
    "NestedResourcesTransformer",
]


from dataclasses import dataclass, replace
from typing import Dict, List, Type, cast

from beet import Context, DataModelBase, NamespaceFile
from beet.core.utils import JsonDict, required_field, snake_case
from tokenstream import set_location

from mecha import (
    AstChildren,
    AstCommand,
    AstJson,
    AstResourceLocation,
    AstRoot,
    CompilationDatabase,
    Diagnostic,
    DiagnosticCollection,
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
    merge_commands = {"merge": {"type": "literal", "children": commands}}
    mc.spec.add_commands({"type": "root", "children": {**commands, **merge_commands}})

    mc.spec.parsers["nested_json"] = delegate("json")
    mc.spec.parsers["command:argument:mecha:nested_json"] = MultilineParser(
        delegate("nested_json")
    )

    mc.transform.extend(
        NestedResourcesTransformer(
            ctx=ctx,
            database=mc.database,
            json_identifiers={
                f"{prefix}{name}:name:content": file_type
                for prefix in ["", "merge:"]
                for name, file_type in json_resources.items()
            },
        )
    )


@dataclass
class NestedResourcesTransformer(MutatingReducer):
    """Transformer that handles nested resources."""

    ctx: Context = required_field()
    database: CompilationDatabase = required_field()

    json_identifiers: Dict[str, Type[NamespaceFile]] = required_field()

    @rule(AstRoot)
    def nested_resources(self, node: AstRoot):
        assets, data = self.ctx.packs

        changed = False
        commands: List[AstCommand] = []

        with DiagnosticCollection() as diagnostics:
            for command in node.commands:
                if file_type := self.json_identifiers.get(command.identifier):
                    name, content = command.arguments

                    if isinstance(name, AstResourceLocation) and isinstance(
                        content, AstJson
                    ):
                        if file_type in assets.namespace_type.field_map:
                            proxy = assets[file_type]
                        else:
                            proxy = data[file_type]

                        if not isinstance(value := content.evaluate(), dict):
                            d = Diagnostic(
                                level="error",
                                message=f"Invalid json object of type {type(value)}.",
                            )
                            diagnostics.add(set_location(d, content))
                            continue

                        full_name = name.get_canonical_value()
                        file_instance = file_type(
                            cast(JsonDict, value),
                            original=self.database.current.original,
                        )

                        if command.identifier.startswith("merge:"):
                            proxy.merge({full_name: file_instance})
                        elif full_name not in proxy:
                            proxy[full_name] = file_instance
                        else:
                            d = Diagnostic(
                                level="error",
                                message=f"Resource {full_name!r} of type {file_type} already exists.",
                            )
                            diagnostics.add(set_location(d, name))
                            continue

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
