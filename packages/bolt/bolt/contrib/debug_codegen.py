"""Plugin for emitting generated code."""


__all__ = [
    "DebugCodegenEmitter",
]


from dataclasses import dataclass

from beet import Context
from beet.core.utils import required_field
from mecha import AstRoot, Mecha, Visitor, rule

from bolt import Runtime
from bolt.module import ModuleManager


def beet_default(ctx: Context):
    mc = ctx.inject(Mecha)
    runtime = ctx.inject(Runtime)
    mc.steps[:] = [DebugCodegenEmitter(modules=runtime.modules)]


@dataclass
class DebugCodegenEmitter(Visitor):
    """Visitor that interrupts the compilation process and dumps the generated code."""

    modules: ModuleManager = required_field()

    @rule(AstRoot)
    def debug_codegen(self, node: AstRoot):
        self.modules.database.current.text = self.modules.codegen(node).source or ""
        return None
