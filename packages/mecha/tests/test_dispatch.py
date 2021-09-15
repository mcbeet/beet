from typing import List, Type

from mecha import AstNumber, Mecha, Visitor, rule
from mecha.ast import (
    AstCommand,
    AstCoordinate,
    AstDustParticleParameters,
    AstNode,
    AstParticle,
    AstResourceLocation,
    AstVector3,
)


def test_visitor(mc: Mecha):
    ast = mc.parse_function("particle dust 1.0 0.5 0.5 1.0 7 7 7")

    numbers: List[AstNode] = []

    visitor = Visitor()
    visitor.add_rule(rule(AstNumber)(numbers.append))
    visitor.invoke(ast)

    assert numbers == [
        AstNumber(value=1),
        AstNumber(value=0.5),
        AstNumber(value=0.5),
        AstNumber(value=1),
    ]


def test_visitor_extend(mc: Mecha):
    ast = mc.parse_command("particle dust 1.0 0.5 7 1.0 7 7 7")

    nodes: List[Type[AstNode]] = []
    numbers: List[AstNumber] = []
    sevens: List[AstNumber] = []

    class Foo(Visitor):
        @rule
        def default(self, node: AstNode):
            nodes.append(type(node))
            yield from node

        @rule(AstNumber, value=7)
        def seven(self, node: AstNumber):
            sevens.append(node)

    visitor = Visitor()
    visitor.extend(rule(AstNumber)(numbers.append), Foo())
    visitor.invoke(ast)

    print(visitor.rules)

    assert nodes == [
        AstCommand,
        AstParticle,
        AstResourceLocation,
        AstDustParticleParameters,
        AstVector3,
        AstCoordinate,
        AstCoordinate,
        AstCoordinate,
    ]

    assert numbers == [AstNumber(value=1), AstNumber(value=0.5), AstNumber(value=1)]
    assert sevens == [AstNumber(value=7)]
