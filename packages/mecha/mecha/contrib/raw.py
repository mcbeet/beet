"""Plugin for inserting raw commands."""


__all__ = [
    "RawCommandSerializer",
]


from typing import List

from beet import Context

from mecha import AstCommand, AstGreedy, Mecha, Visitor, rule

RAW_COMMAND_TREE = {
    "type": "root",
    "children": {
        "raw": {
            "type": "literal",
            "children": {
                "value": {
                    "type": "argument",
                    "executable": True,
                    "parser": "brigadier:string",
                    "properties": {
                        "type": "greedy",
                    },
                }
            },
        },
    },
}


def beet_default(ctx: Context):
    mc = ctx.inject(Mecha)
    mc.spec.add_commands(RAW_COMMAND_TREE)
    mc.serialize.extend(RawCommandSerializer())


class RawCommandSerializer(Visitor):
    @rule(AstCommand, identifier="raw:value")
    def raw_command(self, node: AstCommand, result: List[str]):
        if isinstance(command := node.arguments[0], AstGreedy):
            result.append(command.value)
