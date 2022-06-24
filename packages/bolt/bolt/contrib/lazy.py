"""Plugin for importing bolt modules lazily."""


__all__ = [
    "LazyFilter",
    "BoltLazyOptions",
    "bolt_lazy",
]


from dataclasses import dataclass
from functools import partial
from typing import Any

from beet import Context, ListOption, TextFileBase, configurable
from beet.core.utils import required_field
from mecha import CompilationDatabase, Mecha, Visitor, rule
from pathspec import PathSpec
from pydantic import BaseModel

from bolt import AstModuleRoot, Runtime


class BoltLazyOptions(BaseModel):
    match: ListOption[str] = ListOption()


def beet_default(ctx: Context):
    ctx.require(bolt_lazy)


@configurable(validator=BoltLazyOptions)
def bolt_lazy(ctx: Context, opts: BoltLazyOptions):
    """Plugin for importing bolt modules lazily."""
    mc = ctx.inject(Mecha)
    runtime = ctx.inject(Runtime)

    mc.steps.insert(
        mc.steps.index(runtime.evaluate),
        LazyFilter(
            runtime=runtime,
            database=mc.database,
            path_spec=PathSpec.from_lines("gitwildmatch", opts.match.entries()),
        ),
    )


@dataclass
class LazyFilter(Visitor):
    """Visitor that filters lazy modules from the compilation by matching resource location."""

    runtime: Runtime = required_field()
    database: CompilationDatabase = required_field()
    path_spec: PathSpec = required_field()

    @rule(AstModuleRoot)
    def lazy_module(self, node: AstModuleRoot):
        module = self.runtime.get_module(node)
        path = module.resource_location

        if path and self.path_spec.match_file(path):
            module.execution_hooks.append(
                partial(
                    self.restore_lazy,
                    self.database.current,
                    node,
                    self.database.step + 1,
                )
            )
            return None

        return node

    def restore_lazy(self, key: TextFileBase[Any], node: AstModuleRoot, step: int):
        compilation_unit = self.database[key]
        compilation_unit.ast = node
        self.database.enqueue(key, step)
