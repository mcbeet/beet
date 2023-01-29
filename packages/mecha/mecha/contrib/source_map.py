"""Plugin that emits source mapping information."""


__all__ = [
    "AstSourceMap",
    "SourceMapOptions",
    "SourceMapTransformer",
    "SourceMapSerializer",
    "source_map",
]


from dataclasses import dataclass, replace
from typing import List

from beet import Context, configurable
from beet.core.utils import required_field
from jinja2 import Template
from pydantic import BaseModel

from mecha import (
    AstChildren,
    AstCommandSentinel,
    AstRoot,
    CompilationDatabase,
    Mecha,
    MutatingReducer,
    Visitor,
    rule,
)


class SourceMapOptions(BaseModel):
    header: str = "# [source_map] {{ compilation_unit.filename or compilation_unit.resource_location }}"

    class Config:
        extra = "forbid"


def beet_default(ctx: Context):
    ctx.require(source_map)


@configurable(validator=SourceMapOptions)
def source_map(ctx: Context, opts: SourceMapOptions):
    mc = ctx.inject(Mecha)
    mc.transform.extend(
        SourceMapTransformer(
            database=mc.database,
            header_template=ctx.template.compile(opts.header),
        )
    )
    mc.serialize.extend(SourceMapSerializer())


@dataclass(frozen=True, slots=True)
class AstSourceMap(AstCommandSentinel):
    """Ast source map node."""

    header: str = required_field()

    compile_hints = {"skip_execute_inline_single_command": True}


@dataclass
class SourceMapTransformer(MutatingReducer):
    database: CompilationDatabase = required_field()
    header_template: Template = required_field()

    @rule(AstRoot)
    def insert_source_map(self, node: AstRoot):
        if not node.commands or not isinstance(node.commands[0], AstSourceMap):
            file_instance = self.database.current
            source_map = AstSourceMap(
                header=self.header_template.render(
                    file_instance=file_instance,
                    compilation_unit=self.database[file_instance],
                )
            )
            node = replace(node, commands=AstChildren([source_map, *node.commands]))
        return node


class SourceMapSerializer(Visitor):
    @rule(AstSourceMap)
    def source_map(self, node: AstSourceMap, result: List[str]):
        result.append(node.header)
