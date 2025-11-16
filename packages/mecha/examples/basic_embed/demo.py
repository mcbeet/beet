from dataclasses import dataclass, replace
from typing import Generator

from beet import Context, LootTable
from beet.core.utils import required_field
from nbtlib import String

from mecha import (
    AbstractNode,
    AstChildren,
    AstJson,
    AstJsonObject,
    AstJsonObjectEntry,
    AstJsonObjectKey,
    AstJsonValue,
    AstNbt,
    AstNbtCompoundEntry,
    AstNbtCompoundKey,
    AstNbtValue,
    CompilationDatabase,
    Mecha,
    MutatingReducer,
    rule,
)
from mecha.contrib.embed import EmbedHandler
from mecha.contrib.json_files import AstJsonRoot


def beet_default(ctx: Context):
    mc = ctx.inject(Mecha)
    embed_handler = ctx.inject(EmbedHandler)

    mc.steps.insert(
        mc.steps.index(mc.transform) + 1,
        LootTableEmbedParser(database=mc.database, embed_handler=embed_handler),
    )
    mc.steps.insert(mc.steps.index(embed_handler.resolver), CustomSubstitutions())


@dataclass
class LootTableEmbedParser(MutatingReducer):
    database: CompilationDatabase = required_field()
    embed_handler: EmbedHandler = required_field()

    def filter(self, node: AbstractNode) -> bool:
        return isinstance(node, AstJsonRoot) and isinstance(
            self.database.current, LootTable
        )

    @rule(AstJsonObject)
    def set_nbt(
        self,
        node: AstJsonObject,
    ) -> Generator[AstJson, AstJson, AstJsonObject]:
        match {entry.key.value: entry for entry in node.entries}:
            case {
                "function": AstJsonObjectEntry(
                    value=AstJsonValue(value="minecraft:set_nbt")
                ) as function,
                "tag": tag,
                **kwargs,
            }:
                parsed_value = self.embed_handler.parse(tag.value, using="nbt_compound")
                if parsed_value is tag.value:
                    return node
                parsed_value = yield parsed_value
                return replace(
                    node,
                    entries=AstChildren(
                        [function, replace(tag, value=parsed_value), *kwargs.values()]
                    ),
                )
            case _:
                return node

    @rule(AstNbtCompoundEntry, key=AstNbtCompoundKey(value="json_text_component"))
    def json_text_component(
        self,
        node: AstNbtCompoundEntry,
    ) -> Generator[AstNbt, AstNbt, AstNbtCompoundEntry]:
        parsed_value = self.embed_handler.parse(node.value, using="json")
        if parsed_value is node.value:
            return node
        parsed_value = yield parsed_value
        return replace(node, value=parsed_value)


class CustomSubstitutions(MutatingReducer):
    @rule(AstNbtValue, value="$PLACEHOLDER")
    def replace_placeholder(self, node: AstNbtValue):
        return replace(node, value=String("owo"))

    @rule(
        AstJsonObjectEntry,
        key=AstJsonObjectKey(value="color"),
        value=AstJsonValue(value="aqua"),
    )
    def replace_color_aqua(self, node: AstJsonObjectEntry):
        return replace(node, value=replace(node.value, value="red"))
