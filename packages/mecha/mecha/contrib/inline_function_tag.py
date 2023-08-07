"""Plugin for declaring function tags inline."""


__all__ = [
    "InlineFunctionTagHandler",
]


import logging
from dataclasses import dataclass, replace
from importlib.resources import files
from typing import List

from beet import Context, FunctionTag, Generator
from beet.core.utils import required_field
from tokenstream import set_location

from mecha import (
    AstChildren,
    AstCommand,
    AstResourceLocation,
    AstRoot,
    CommandTree,
    CompilationDatabase,
    Diagnostic,
    Mecha,
    Visitor,
    rule,
)

logger = logging.getLogger(__name__)


def beet_default(ctx: Context):
    logger.warning('Deprecated in favor of "mecha.contrib.nested_resources".')

    mc = ctx.inject(Mecha)

    commands_json = (
        files("mecha.resources").joinpath("inline_function_tag.json").read_text()
    )
    mc.spec.add_commands(CommandTree.parse_raw(commands_json))

    mc.transform.extend(inline_execute_function_tag)
    mc.steps.insert(
        mc.steps.index(mc.transform) + 1,
        InlineFunctionTagHandler(generate=ctx.generate, database=mc.database),
    )


@rule(AstCommand, identifier="execute:run:subcommand")
def inline_execute_function_tag(node: AstCommand):
    if isinstance(command := node.arguments[0], AstCommand):
        if command.identifier == "function:tag:name":
            d = Diagnostic("error", "Can't add function tag with execute.")
            yield set_location(d, command.arguments[0])
    return node


@dataclass
class InlineFunctionTagHandler(Visitor):
    """Handler for inline function tags."""

    generate: Generator = required_field()
    database: CompilationDatabase = required_field()

    @rule(AstRoot)
    def inline_function_tag(self, node: AstRoot):
        changed = False
        commands: List[AstCommand] = []

        for command in node.commands:
            if command.identifier == "function:tag:name" and isinstance(
                tag := command.arguments[0], AstResourceLocation
            ):
                changed = True
                if path := self.database[self.database.current].resource_location:
                    self.generate(
                        tag.get_canonical_value(), merge=FunctionTag({"values": [path]})
                    )
                else:
                    d = Diagnostic("error", "No current path to add function tag.")
                    yield set_location(d, tag)
                    return node
            else:
                commands.append(command)

        if changed:
            return replace(node, commands=AstChildren(commands))

        return node
