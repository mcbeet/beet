__all__ = [
    "Serializer",
]


import json
from typing import Any, Iterable, Iterator, List

from .ast import (
    AstBlock,
    AstBlockState,
    AstChildren,
    AstCommand,
    AstCoordinate,
    AstItem,
    AstJson,
    AstMessage,
    AstNbt,
    AstNbtPath,
    AstNbtPathSubscript,
    AstNode,
    AstParticle,
    AstParticleParameters,
    AstRange,
    AstResourceLocation,
    AstRoot,
    AstSelector,
    AstSelectorAdvancementMatch,
    AstSelectorAdvancementPredicateMatch,
    AstSelectorAdvancements,
    AstSelectorArgument,
    AstSelectorScoreMatch,
    AstSelectorScores,
    AstTime,
    AstValue,
    AstVector2,
    AstVector3,
)
from .dispatch import Visitor, rule
from .spec import CommandSpec


class Serializer(Visitor):
    spec: CommandSpec

    def __init__(self, spec: CommandSpec):
        super().__init__()
        self.spec = spec

    def __call__(self, node: AstNode) -> str:
        result: List[str] = []
        self.invoke(node, result)
        return "".join(result)

    def collection(
        self,
        nodes: Iterable[AstNode],
        delimitters: str,
        result: List[str],
    ) -> Iterator[AstNode]:
        """Helper for serializing collections."""
        result.append(delimitters[0])
        sep = ""
        for node in nodes:
            result.append(sep)
            sep = ", "
            yield node
        result.append(delimitters[-1])

    def key_value(self, node: Any, sep: str, result: List[str]) -> Iterator[AstNode]:
        """Helper for serializing key-value pairs."""
        yield node.key
        result.append(sep)
        yield node.value

    @rule(AstRoot)
    def root(self, node: AstRoot, result: List[str], *args: Any):
        for command in node.commands:
            yield command
            result.append("\n")

    @rule(AstCommand)
    def command(self, node: AstCommand, result: List[str]):
        prototype = self.spec.prototypes[node.identifier]
        argument_index = 0

        sep = ""
        for token in prototype.signature:
            result.append(sep)
            sep = " "

            if isinstance(token, str):
                result.append(token)
            else:
                yield node.arguments[argument_index]
                argument_index += 1

    @rule(AstValue)
    def value(self, node: AstValue[Any], result: List[str]):
        value = str(node.value)
        if isinstance(node.value, bool):
            value = value.lower()
        result.append(value)

    @rule(AstCoordinate)
    def coordinate(self, node: AstCoordinate, result: List[str]):
        if node.type == "relative":
            result.append("~")
            if node.value == 0:
                return
        elif node.type == "local":
            result.append("^")
            if node.value == 0:
                return
        result.append(str(node.value))

    @rule(AstVector2)
    def vector2(self, node: AstVector2, result: List[str]):
        yield node.x
        result.append(" ")
        yield node.y

    @rule(AstVector3)
    def vector3(self, node: AstVector3, result: List[str]):
        yield node.x
        result.append(" ")
        yield node.y
        result.append(" ")
        yield node.z

    @rule(AstJson)
    def json(self, node: AstJson, result: List[str]):
        result.append(json.dumps(node.evaluate()))

    @rule(AstNbt)
    def nbt(self, node: AstNbt, result: List[str]):
        result.append(node.evaluate().snbt())

    @rule(AstResourceLocation)
    def resource_location(self, node: AstResourceLocation, result: List[str]):
        if node.is_tag:
            result.append("#")
        if node.namespace:
            yield node.namespace
            result.append(":")
        yield node.path

    @rule(AstBlockState)
    def block_state(self, node: AstBlockState, result: List[str]):
        yield from self.key_value(node, "=", result)

    @rule(AstBlock)
    def block(self, node: AstBlock, result: List[str]):
        yield node.identifier
        if node.block_states:
            yield from self.collection(node.block_states, "[]", result)
        if node.data_tags:
            yield node.data_tags

    @rule(AstItem)
    def item(self, node: AstItem, result: List[str]):
        yield node.identifier
        if node.data_tags:
            yield node.data_tags

    @rule(AstRange)
    def range(self, node: AstRange, result: List[str]):
        if node.exact:
            result.append(str(node.value))
        else:
            if node.min:
                result.append(str(node.min))
            result.append("..")
            if node.max:
                result.append(str(node.max))

    @rule(AstTime)
    def time(self, node: AstTime, result: List[str]):
        result.append(str(node.value))

        if node.unit == "day":
            result.append("d")
        elif node.unit == "second":
            result.append("s")

    @rule(AstSelectorScoreMatch)
    @rule(AstSelectorAdvancementPredicateMatch)
    def selector_argument_key_value(self, node: AstNode, result: List[str]):
        yield from self.key_value(node, "=", result)

    @rule(AstSelectorScores)
    def selector_scores(self, node: AstSelectorScores, result: List[str]):
        yield from self.collection(node.scores, "{}", result)

    @rule(AstSelectorAdvancementMatch)
    def selector_advancement_match(
        self,
        node: AstSelectorAdvancementMatch,
        result: List[str],
    ):
        yield node.key
        result.append("=")
        if isinstance(node.value, AstChildren):
            yield from self.collection(node.value, "{}", result)
        else:
            yield node.value

    @rule(AstSelectorAdvancements)
    def selector_advancements(self, node: AstSelectorAdvancements, result: List[str]):
        yield from self.collection(node.advancements, "{}", result)

    @rule(AstSelectorArgument)
    def selector_argument(self, node: AstSelectorArgument, result: List[str]):
        yield node.key
        result.append("=")
        if node.inverted:
            result.append("!")
        yield node.value

    @rule(AstSelector)
    def selector(self, node: AstSelector, result: List[str]):
        result.append("@")
        result.append(node.variable)
        if node.arguments:
            yield from self.collection(node.arguments, "[]", result)

    @rule(AstMessage)
    def message(self, node: AstMessage, result: List[str]):
        sep = ""
        for word in node.words:
            result.append(sep)
            sep = " "
            yield word

    @rule(AstNbtPathSubscript)
    def nbt_path_subscript(self, node: AstNbtPathSubscript, result: List[str]):
        result.append("[")
        if node.index:
            yield node.index
        result.append("]")

    @rule(AstNbtPath)
    def nbt_path(self, node: AstNbtPath, result: List[str]):
        sep = ""
        for component in node.components:
            if isinstance(component, AstValue):
                result.append(sep)
            sep = "."
            yield component

    @rule(AstParticleParameters)
    def particle_parameters(self, node: AstParticleParameters, result: List[str]):
        sep = ""
        for param in node:
            result.append(sep)
            sep = " "
            yield param

    @rule(AstParticle)
    def particle(self, node: AstParticle, result: List[str]):
        yield node.name
        if node.parameters:
            result.append(" ")
            yield node.parameters
