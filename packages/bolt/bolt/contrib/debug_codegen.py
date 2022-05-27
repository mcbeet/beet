"""Plugin for emitting generated code."""


__all__ = [
    "DebugCodegenEmitter",
]


from dataclasses import dataclass

from beet import Context
from beet.core.utils import required_field
from mecha import AstRoot, CompilationDatabase, Mecha, Visitor, rule

from bolt import Runtime


def beet_default(ctx: Context):
    mc = ctx.inject(Mecha)
    runtime = ctx.inject(Runtime)
    mc.steps[:] = [DebugCodegenEmitter(runtime=runtime, database=mc.database)]


@dataclass
class DebugCodegenEmitter(Visitor):
    """Visitor that interrupts the compilation process and dumps the generated code."""

    runtime: Runtime = required_field()
    database: CompilationDatabase = required_field()

    @rule(AstRoot)
    def debug_codegen(self, node: AstRoot):
        self.database.current.text = self.runtime.codegen(node)[0] or ""
        return None
