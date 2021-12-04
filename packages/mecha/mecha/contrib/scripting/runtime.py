__all__ = [
    "Runtime",
    "Module",
    "ModuleCacheBackend",
    "Evaluator",
]


import marshal
from contextlib import contextmanager
from dataclasses import dataclass, field
from importlib.resources import read_text
from io import BufferedReader, BufferedWriter
from pathlib import Path
from types import CodeType
from typing import Any, Dict, Iterator, List, Optional, Union

from beet import Context, TextFileBase
from beet.core.utils import JsonDict, required_field

from mecha import (
    AstCacheBackend,
    AstCommand,
    AstRoot,
    CommandTree,
    CompilationDatabase,
    Dispatcher,
    Mecha,
    Visitor,
    rule,
)

from .codegen import Codegen
from .helpers import get_scripting_helpers
from .parse import get_scripting_parsers


@dataclass
class Module:
    """Class holding the state of a compiled module."""

    ast: AstRoot
    code: Optional[CodeType]
    refs: List[Any]
    output: Optional[str]
    namespace: JsonDict = field(default_factory=dict)


class Runtime:
    """The scripting runtime."""

    directory: Path
    database: CompilationDatabase
    codegen: Codegen
    evaluate: Dispatcher[AstRoot]
    modules: Dict[TextFileBase[Any], Module]
    commands: List[AstCommand]
    helpers: Dict[str, Any]

    def __init__(self, ctx: Union[Context, Mecha]):
        if isinstance(ctx, Context):
            ctx.require(
                "mecha.contrib.relative_location",
                "mecha.contrib.nesting",
                "mecha.contrib.implicit_execute",
            )
            mc = ctx.inject(Mecha)
        else:
            mc = ctx

        commands_json = read_text("mecha.contrib.scripting.resources", "commands.json")
        mc.spec.add_commands(CommandTree.parse_raw(commands_json))
        mc.spec.parsers.update(get_scripting_parsers(mc.spec.parsers))

        self.directory = mc.directory
        self.database = mc.database
        self.codegen = Codegen(spec=mc.spec)

        self.evaluate = Evaluator(runtime=self)
        mc.steps.insert(0, self.evaluate)

        self.modules = {}
        self.commands = []
        self.helpers = get_scripting_helpers()

        mc.cache_backend = ModuleCacheBackend(self)

    def get_module(
        self,
        node: AstRoot,
        file_instance: Optional[TextFileBase[Any]] = None,
    ) -> Module:
        """Return an executable module for the given ast."""
        if file_instance is None:
            file_instance = self.database.current

        module = self.modules.get(file_instance)
        if module and module.ast is node:
            return module

        source, output, refs = self.codegen(node)

        if source and output:
            if filename := self.database[file_instance].filename:
                filename = str(self.directory / filename)
            else:
                filename = "<mecha>"

            code = compile(source, filename, "exec")

        else:
            code = None

        module = Module(node, code, refs, output)
        self.modules[file_instance] = module

        return module

    def get_output(self, module: Module) -> AstRoot:
        """Run the module and return the output ast."""
        if not module.code or not module.output:
            return module.ast
        if module.output in module.namespace:
            return module.namespace[module.output]

        module.namespace["_mecha_runtime"] = self
        module.namespace["_mecha_refs"] = module.refs
        module.namespace["__file__"] = module.code.co_filename

        exec(module.code, module.namespace)

        return module.namespace[module.output]

    @contextmanager
    def scope(
        self,
        commands: Optional[List[AstCommand]] = None,
    ) -> Iterator[List[AstCommand]]:
        """Create a new scope to gather commands."""
        if commands is None:
            commands = []

        previous_commands = self.commands
        self.commands = commands

        try:
            yield commands
        finally:
            self.commands = previous_commands


@dataclass
class ModuleCacheBackend(AstCacheBackend):
    """Cache backend that also restores the generated modules."""

    runtime: Runtime

    def load(self, f: BufferedReader) -> AstRoot:
        data = self.load_data(f)
        ast = data["ast"]

        self.runtime.modules[self.runtime.database.current] = Module(
            ast=ast,
            code=marshal.load(f),
            refs=data["refs"],
            output=data["output"],
        )

        return ast

    def dump(self, node: AstRoot, f: BufferedWriter):
        module = self.runtime.get_module(node)

        self.dump_data(
            {
                "ast": module.ast,
                "refs": module.refs,
                "output": module.output,
            },
            f,
        )

        marshal.dump(module.code, f)


@dataclass
class Evaluator(Visitor):
    """Visitor that evaluates modules."""

    runtime: Runtime = required_field()

    @rule(AstRoot)
    def root(self, node: AstRoot) -> AstRoot:
        module = self.runtime.get_module(node)
        return self.runtime.get_output(module)
