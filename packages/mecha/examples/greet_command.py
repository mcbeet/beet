from dataclasses import replace
from typing import cast

from mecha import (
    AstChildren,
    AstCommand,
    AstLiteral,
    AstMessage,
    AstSelector,
    Mecha,
    MutatingReducer,
    rule,
)

mc = Mecha()

mc.spec.add_commands(
    {
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
)

function = """
    greet @a[
        tag = !registered
    ]
"""

ast = mc.parse(function, multiline=True)
print(ast.dump())
print(mc.serialize(ast))


@rule(AstCommand, identifier="greet:entity")
def rewrite_greet_command(node: AstCommand) -> AstCommand:
    return replace(
        node,
        identifier="say:message",
        arguments=AstChildren(
            [
                AstMessage(
                    fragments=AstChildren(
                        [
                            AstLiteral(value="Hello "),
                            cast(AstSelector, node.arguments[0]),
                        ]
                    )
                )
            ]
        ),
    )


transform = MutatingReducer()
transform.extend(rewrite_greet_command)

ast = transform(ast)
print(ast.dump())
print(mc.serialize(ast))

print(ast == mc.parse("say Hello @a[tag=!registered]"))  # True
print(mc.parse("execute if score #init temp = #wat temp run greet @a[tag=hi]").dump())
