from dataclasses import dataclass

from beet import Context, LootTable
from beet.core.utils import required_field
from tokenstream import set_location

from mecha import (
    AbstractNode,
    AstChildren,
    AstJsonArray,
    AstJsonValue,
    CompilationDatabase,
    Mecha,
    MutatingReducer,
    rule,
)
from mecha.contrib.json_files import AstJsonRoot


def beet_default(ctx: Context):
    mc = ctx.inject(Mecha)
    mc.steps.insert(
        mc.steps.index(mc.transform) + 1,
        EmptyLootTableTransformer(database=mc.database),
    )


@dataclass
class EmptyLootTableTransformer(MutatingReducer):
    database: CompilationDatabase = required_field()

    def filter(self, node: AbstractNode) -> bool:
        return isinstance(node, AstJsonRoot) and isinstance(
            self.database.current, LootTable
        )

    @rule(AstJsonValue, value="empty")
    def empty(self, node: AstJsonValue):
        return set_location(AstJsonArray(elements=AstChildren()), node)
