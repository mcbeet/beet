"""Plugin that handles implicit execute commands."""


__all__ = [
    "ImplicitExecuteNormalizer",
]


from dataclasses import dataclass, replace
from typing import Set, cast

from beet import Context
from beet.core.utils import required_field
from tokenstream import set_location

from mecha import AstChildren, AstCommand, AstNode, Mecha, MutatingReducer, rule


def beet_default(ctx: Context):
    mc = ctx.inject(Mecha)

    if execute := mc.spec.tree.get("execute"):
        commands = {literal for literal, _ in mc.spec.tree.get_all_literals()}
        commands.discard("execute")

        shorthands = {literal for literal, _ in execute.get_all_literals()}
        shorthands.discard("run")

        commands, shorthands = commands - shorthands, shorthands - commands

        mc.spec.add_commands(
            {
                "type": "root",
                "children": {
                    "execute": {
                        "type": "literal",
                        "children": {
                            literal: {"type": "literal", "redirect": [literal]}
                            for literal in commands
                        },
                    },
                    **{
                        literal: {"type": "literal", "redirect": ["execute", literal]}
                        for literal in shorthands
                    },
                },
            }
        )

        mc.normalize.extend(
            ImplicitExecuteNormalizer(
                commands=commands,
                shorthands=shorthands,
            )
        )


@dataclass
class ImplicitExecuteNormalizer(MutatingReducer):
    """Normalizer that replaces implicit execute shorthands with the full command."""

    commands: Set[str] = required_field()
    shorthands: Set[str] = required_field()

    @rule(AstCommand)
    def implicit_execute(self, node: AstCommand) -> AstCommand:
        prefix, _, identifier = node.identifier.partition(":")

        if prefix == "execute" and identifier.partition(":")[0] in self.commands:
            subcommand = replace(node, identifier=identifier)
            run = AstCommand(
                identifier="execute:run:subcommand",
                arguments=AstChildren([cast(AstNode, subcommand)]),
            )
            return set_location(run, node)

        elif prefix in self.shorthands:
            subcommand = replace(node, identifier=f"execute:{node.identifier}")
            execute = AstCommand(
                identifier="execute:subcommand",
                arguments=AstChildren([cast(AstNode, subcommand)]),
            )
            return set_location(execute, node)

        return node
