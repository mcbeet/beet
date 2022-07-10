__all__ = [
    "Runtime",
    "Evaluator",
    "check_toplevel_commands",
    "UnusableCompilationUnit",
]


import builtins
from contextlib import contextmanager
from dataclasses import dataclass
from importlib.resources import read_text
from typing import Any, Callable, Dict, Iterator, List, Optional, Set, Union

from beet import BubbleException, Context, generate_tree
from beet.core.utils import JsonDict, required_field
from mecha import (
    AstCommand,
    AstRoot,
    CommandTree,
    CompilationError,
    Diagnostic,
    DiagnosticCollection,
    Dispatcher,
    Mecha,
    Visitor,
    rule,
)
from tokenstream import set_location

from .ast import AstModuleRoot
from .codegen import Codegen
from .helpers import get_bolt_helpers
from .loop_info import loop_info
from .module import (
    CompiledModule,
    Module,
    ModuleCacheBackend,
    ModuleManager,
    UnusableCompilationUnit,
)
from .parse import get_bolt_parsers
from .utils import internal


class Runtime:
    """The bolt runtime."""

    commands: List[AstCommand]
    helpers: Dict[str, Any]
    globals: JsonDict
    builtins: Set[str]

    modules: ModuleManager
    evaluate: Dispatcher[AstRoot]

    def __init__(self, ctx: Union[Context, Mecha]):
        self.commands = []
        self.helpers = get_bolt_helpers()
        self.globals = {"_bolt_runtime": self, "ctx": None, "loop_info": loop_info}
        self.builtins = {name for name in dir(builtins) if not name.startswith("_")}

        if isinstance(ctx, Context):
            ctx.require(
                "mecha.contrib.relative_location",
                "mecha.contrib.inline_function_tag",
                "mecha.contrib.nesting",
                "mecha.contrib.nested_resources",
                "mecha.contrib.nested_yaml",
                "mecha.contrib.implicit_execute",
                self.finalize,
            )

            ctx.data.extend_namespace.append(Module)

            self.globals["ctx"] = ctx

            self.expose("generate_path", ctx.generate.path)
            self.expose("generate_id", ctx.generate.id)
            self.expose("generate_hash", ctx.generate.hash)
            self.expose("generate_objective", ctx.generate.objective)
            self.expose(
                "generate_tree",
                lambda *args, **kwargs: generate_tree(
                    (
                        root := kwargs.pop("root")
                        if "root" in kwargs
                        else self.modules.current_path
                    ),
                    *args,
                    name=(
                        kwargs.pop("name")
                        if "name" in kwargs
                        else ctx.generate["tree"][root].format("tree_{incr}")
                    ),
                    **kwargs,
                ),
            )

            mc = ctx.inject(Mecha)

        else:
            mc = ctx

        self.modules = ModuleManager(
            directory=mc.directory,
            database=mc.database,
            codegen=Codegen(),
            globals=self.globals,
            builtins=self.builtins,
        )

        self.evaluate = Evaluator(modules=self.modules)

        mc.providers.append(Module)

        commands_json = read_text("bolt.resources", "commands.json")
        mc.spec.add_commands(CommandTree.parse_raw(commands_json))
        mc.spec.parsers.update(get_bolt_parsers(mc.spec.parsers, self.modules))

        mc.steps.insert(0, self.evaluate)

        mc.serialize.extend(check_toplevel_commands)
        mc.cache_backend = ModuleCacheBackend(modules=self.modules)

    def expose(self, name: str, function: Callable[..., Any]):
        """Expose a utility function."""
        self.globals[name] = lambda *args, **kwargs: function(*args, **kwargs)  # type: ignore

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

    @internal
    def import_module(self, resource_location: str) -> CompiledModule:
        """Import module."""
        try:
            module = self.modules[resource_location]
        except KeyError:
            msg = f'Couldn\'t import "{resource_location}".'
            raise ImportError(msg) from None
        if not module.executing:
            self.modules.eval(module)
        return module

    @internal
    def from_module_import(self, resource_location: str, *args: str) -> Any:
        """Import a specific name from a module."""
        module = self.import_module(resource_location)
        try:
            values = [module.namespace[name] for name in args]
        except KeyError as exc:
            msg = f'Couldn\'t import {exc} from "{resource_location}".'
            raise ImportError(msg) from None
        return values[0] if len(values) == 1 else values

    def finalize(self, ctx: Context):
        """Plugin that removes modules at the end of the build."""
        yield
        ctx.data[Module].clear()


@dataclass
class Evaluator(Visitor):
    """Visitor that evaluates modules."""

    modules: ModuleManager = required_field()

    @rule(AstRoot)
    def root(self, node: AstRoot) -> AstRoot:
        module = self.modules.for_current_ast(node)
        try:
            return self.modules.eval(module)
        except BubbleException:
            raise
        except UnusableCompilationUnit as exc:
            if not exc.compilation_unit.diagnostics.error:
                raise
            raise DiagnosticCollection()
        except Exception as exc:
            msg = "Top-level statement raised an exception."
            if module.resource_location:
                msg += f" ({module.resource_location})"
            tb = exc.__traceback__.tb_next.tb_next  # type: ignore
            raise CompilationError(msg) from exc.with_traceback(tb)


@rule(AstModuleRoot)
def check_toplevel_commands(node: AstModuleRoot, result: List[str]):
    """Emit diagnostic if module has toplevel commands."""
    if node.commands:
        command = node.commands[0]
        name = command.identifier.partition(":")[0]
        raise set_location(
            Diagnostic("warn", f'Standalone "{name}" command in module.'),
            command,
            command.arguments[0] if command.arguments else command,
        )
