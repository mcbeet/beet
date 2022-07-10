"""Plugin for importing bolt modules lazily."""


__all__ = [
    "LazyExecution",
    "LazyFilter",
    "BoltLazyOptions",
    "bolt_lazy",
]


from dataclasses import InitVar, dataclass, field
from functools import partial
from typing import Any, List

from beet import Context, ListOption, TextFileBase, configurable
from beet.core.utils import extra_field, required_field
from mecha import Mecha, Visitor, rule
from pathspec import PathSpec
from pydantic import BaseModel

from bolt import AstModuleRoot, ModuleManager, Runtime


class BoltLazyOptions(BaseModel):
    match: ListOption[str] = ListOption()


def beet_default(ctx: Context):
    ctx.require(bolt_lazy)


@configurable(validator=BoltLazyOptions)
def bolt_lazy(ctx: Context, opts: BoltLazyOptions):
    """Plugin for importing bolt modules lazily."""
    lazy = ctx.inject(LazyExecution)
    lazy.register(*opts.match.entries())


@dataclass
class LazyExecution:
    """Service for managing lazy execution."""

    ctx: InitVar[Context]
    match: List[str] = field(default_factory=list)
    path_spec: PathSpec = extra_field(init=False)

    def __post_init__(self, ctx: Context):
        self.register()

        mc = ctx.inject(Mecha)
        runtime = ctx.inject(Runtime)

        mc.steps.insert(
            mc.steps.index(runtime.evaluate),
            LazyFilter(modules=runtime.modules, lazy=self),
        )

    def register(self, *match: str):
        """Make the modules matching the specified patterns lazy."""
        self.match.extend(match)
        self.path_spec = PathSpec.from_lines("gitwildmatch", self.match)

    def check(self, resource_location: str) -> bool:
        """Check if the specified module is lazy."""
        return self.path_spec.match_file(resource_location)


@dataclass
class LazyFilter(Visitor):
    """Visitor that filters lazy modules from the compilation by matching resource location."""

    modules: ModuleManager = required_field()
    lazy: LazyExecution = required_field()

    @rule(AstModuleRoot)
    def lazy_module(self, node: AstModuleRoot):
        module = self.modules.get(node)
        if module.resource_location and self.lazy.check(module.resource_location):
            module.execution_hooks.append(
                partial(
                    self.restore_lazy,
                    self.modules.database.current,
                    node,
                    self.modules.database.step + 1,
                )
            )
            return None
        return node

    def restore_lazy(self, key: TextFileBase[Any], node: AstModuleRoot, step: int):
        compilation_unit = self.modules.database[key]
        compilation_unit.ast = node
        self.modules.database.enqueue(key, step)
