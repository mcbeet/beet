from dataclasses import replace
from typing import cast

from beet import Context

from mecha import (
    AstChildren,
    AstCommand,
    AstMessage,
    AstMessageText,
    AstSelector,
    Mecha,
    MutatingReducer,
    rule,
)

COMMAND_TREE = {
    "type": "root",
    "children": {
        "greet": {
            "type": "literal",
            "children": {
                "entity": {
                    "type": "argument",
                    "parser": "minecraft:entity",
                    "properties": {"amount": "multiple", "type": "players"},
                    "executable": True,
                }
            },
        }
    },
}


def beet_default(ctx: Context):
    mc = ctx.inject(Mecha)
    mc.spec.add_commands(COMMAND_TREE)
    mc.transform.extend(GreetCommandTransformer())


class GreetCommandTransformer(MutatingReducer):
    @rule(AstCommand, identifier="greet:entity")
    def greet_command(self, node: AstCommand) -> AstCommand:
        return replace(
            node,
            identifier="say:message",
            arguments=AstChildren(
                [
                    AstMessage(
                        fragments=AstChildren(
                            [
                                AstMessageText(value="Hello "),
                                cast(AstSelector, node.arguments[0]),
                            ]
                        )
                    )
                ]
            ),
        )
