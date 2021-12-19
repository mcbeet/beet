"""Plugin for declaring function tags inline."""


__all__ = [
    "InlineFunctionTagHandler",
]


from dataclasses import dataclass, replace
from importlib.resources import read_text
from typing import List

from beet import Context, FunctionTag
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


def beet_default(ctx: Context):
    mc = ctx.inject(Mecha)

    commands_json = read_text("mecha.resources", "inline_function_tag.json")
    mc.spec.add_commands(CommandTree.parse_raw(commands_json))

    mc.transform.extend(inline_execute_function_tag)
    mc.steps.insert(
        mc.steps.index(mc.transform) + 1,
        InlineFunctionTagHandler(ctx=ctx, database=mc.database),
    )


@rule(AstCommand, identifier="execute:run:subcommand")
def inline_execute_function_tag(node: AstCommand) -> AstCommand:
    if isinstance(command := node.arguments[0], AstCommand):
        if command.identifier == "function:tag:name":
            d = Diagnostic("error", "Can't add function tag with execute.")
            raise set_location(d, command.arguments[0])
    return node


@dataclass
class InlineFunctionTagHandler(Visitor):
    """Handler for inline function tags."""

    ctx: Context = required_field()
    database: CompilationDatabase = required_field()

    @rule(AstRoot)
    def inline_function_tag(self, node: AstRoot) -> AstRoot:
        changed = False
        commands: List[AstCommand] = []

        for command in node.commands:
            if command.identifier == "function:tag:name" and isinstance(
                tag := command.arguments[0], AstResourceLocation
            ):
                changed = True
                if path := self.database[self.database.current].resource_location:
                    self.ctx.data.function_tags.merge(
                        {tag.get_canonical_value(): FunctionTag({"values": [path]})}
                    )
                else:
                    d = Diagnostic("error", "No current path to add function tag.")
                    raise set_location(d, tag)
            else:
                commands.append(command)

        if changed:
            return replace(node, commands=AstChildren(commands))

        return node
