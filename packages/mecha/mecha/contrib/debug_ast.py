"""Plugin for emitting ast."""


__all__ = [
    "DebugAstOptions",
    "DebugAstEmitter",
    "debug_ast",
]


from dataclasses import dataclass

from beet import Context, configurable
from beet.core.utils import required_field
from pydantic import BaseModel

from mecha import AstRoot, CompilationDatabase, Mecha, Visitor, rule


class DebugAstOptions(BaseModel):
    location: bool = False


def beet_default(ctx: Context):
    ctx.require(debug_ast)


@configurable(validator=DebugAstOptions)
def debug_ast(ctx: Context, opts: DebugAstOptions):
    mc = ctx.inject(Mecha)
    mc.steps[:] = [DebugAstEmitter(location=opts.location, database=mc.database)]


@dataclass
class DebugAstEmitter(Visitor):
    """Visitor that interrupts the compilation process and dumps the current ast."""

    location: bool = False
    database: CompilationDatabase = required_field()

    @rule(AstRoot)
    def debug_ast(self, node: AstRoot):
        exclude = None if self.location else {"location", "end_location"}
        self.database.current.text = node.dump(exclude=exclude) + "\n"
        return None
