"""Plugin that handles implicit execute commands."""


__all__ = [
    "ImplicitExecuteParser",
]


from dataclasses import dataclass, replace
from typing import Any, Set

from beet import Context
from tokenstream import TokenStream, set_location

from mecha import AstChildren, AstCommand, Mecha, Parser


def beet_default(ctx: Context):
    ctx.require("mecha.contrib.nesting")

    mc = ctx.inject(Mecha)

    if execute := mc.spec.tree.get("execute"):
        commands = {literal for literal, _ in mc.spec.tree.get_all_literals()}
        commands -= {"execute", "run"}

        shorthands = {literal for literal, _ in execute.get_all_literals()}
        shorthands -= {"execute", "run"}

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

        mc.spec.parsers["command"] = ImplicitExecuteParser(
            commands=commands,
            shorthands=shorthands,
            parser=mc.spec.parsers["command"],
        )


@dataclass
class ImplicitExecuteParser:
    """Parser that replaces implicit execute shorthands with the full command."""

    commands: Set[str]
    shorthands: Set[str]
    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        if isinstance(node := self.parser(stream), AstCommand):
            match node.identifier.split(":"):
                case ["execute", command, *_] if command in self.commands:
                    subcommand = replace(node, identifier=node.identifier[8:])
                    run = AstCommand(
                        identifier="execute:run:subcommand",
                        arguments=AstChildren([subcommand]),
                    )
                    return set_location(run, node)
                case [shorthand, *_] if shorthand in self.shorthands:
                    subcommand = replace(node, identifier=f"execute:{node.identifier}")
                    execute = AstCommand(
                        identifier="execute:subcommand",
                        arguments=AstChildren([subcommand]),
                    )
                    return set_location(execute, node)
                case _:
                    pass

        return node
