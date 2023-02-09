__all__ = [
    "Runtime",
    "Evaluator",
    "check_toplevel_commands",
]


import builtins
from dataclasses import dataclass, field
from functools import partial
from importlib.resources import files
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Union

from beet import Context, TextFileBase, generate_tree
from beet.core.utils import JsonDict, extra_field, required_field
from mecha import AstRoot, CommandSpec, CommandTree, Diagnostic, Mecha, Visitor, rule
from mecha.contrib.nesting import InplaceNestingPredicate
from pathspec import PathSpec
from tokenstream import set_location

from .ast import AstModuleRoot
from .codegen import Codegen
from .emit import CommandEmitter
from .helpers import get_bolt_helpers
from .loop_info import loop_info
from .memo import MemoHandler, MemoRegistry
from .module import CompiledModule, Module, ModuleCacheBackend, ModuleManager
from .parse import get_bolt_parsers
from .utils import internal


class Runtime(CommandEmitter):
    """The bolt runtime."""

    helpers: Dict[str, Any]
    globals: JsonDict
    builtins: Set[str]

    memo: MemoHandler

    modules: ModuleManager
    evaluate: "Evaluator"

    def __init__(self, ctx: Union[Context, Mecha]):
        super().__init__()
        self.helpers = get_bolt_helpers()
        self.globals = {"_bolt_runtime": self, "ctx": None, "loop_info": loop_info}
        self.builtins = {name for name in dir(builtins) if not name.startswith("_")}

        if isinstance(ctx, Context):
            ctx.require(
                "mecha.contrib.raw",
                "mecha.contrib.relative_location",
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
            self.memo = MemoHandler(
                mc,
                registry=ctx.inject(MemoRegistry),
                generate=ctx.generate,
                inplace_nesting_predicate=ctx.inject(InplaceNestingPredicate),
            )

        else:
            mc = ctx
            self.memo = MemoHandler(mc, MemoRegistry())

        self.modules = ModuleManager(
            directory=mc.directory,
            database=mc.database,
            codegen=Codegen(),
            parse_callback=mc.parse,
            cache=mc.cache,
            globals=self.globals,
            builtins=self.builtins,
        )

        self.evaluate = Evaluator(modules=self.modules)

        mc.providers.append(Module)

        commands_json = files("bolt.resources").joinpath("commands.json").read_text()
        command_tree = CommandTree.parse_raw(commands_json)
        bolt_prototypes = set(CommandSpec(tree=command_tree).prototypes)
        mc.spec.add_commands(command_tree)
        mc.spec.parsers.update(
            get_bolt_parsers(mc.spec.parsers, self.modules, bolt_prototypes)
        )

        mc.steps.insert(0, self.evaluate)

        mc.serialize.extend(check_toplevel_commands)
        mc.cache_backend = ModuleCacheBackend(modules=self.modules)

    def expose(self, name: str, function: Callable[..., Any]):
        """Expose a utility function."""
        self.globals[name] = lambda *args, **kwargs: function(*args, **kwargs)  # type: ignore

    @internal
    def import_module(self, resource_location: str) -> CompiledModule:
        """Import module."""
        module = self.modules.get(resource_location)
        if not module:
            raise ImportError(f'Couldn\'t import "{resource_location}".')
        if not module.executing:
            with self.modules.error_handler(
                "Top-level statement raised an exception.", module.resource_location
            ):
                self.modules.eval(module)
        return module

    @internal
    def from_module_import(self, resource_location: str, *args: str) -> Any:
        """Import a specific name from a module."""
        module = self.import_module(resource_location)
        try:
            values = [module.namespace[name] for name in args]
        except KeyError as exc:
            message = f'Couldn\'t import {exc} from "{resource_location}".'
            raise ImportError(message) from None
        return values[0] if len(values) == 1 else values

    def finalize(self, ctx: Context):
        """Plugin that runs at the end of the build."""
        try:
            yield
        finally:
            ctx.data[Module].clear()
            self.memo.finalize()


@dataclass
class Evaluator(Visitor):
    """Visitor that evaluates modules."""

    modules: ModuleManager = required_field()

    entrypoint: List[str] = field(default_factory=list)
    entrypoint_spec: PathSpec = extra_field(init=False)

    def __post_init__(self):
        super().__post_init__()
        self.add_entrypoint()

    def add_entrypoint(self, *args: Union[str, Iterable[str]]):
        self.entrypoint.extend(
            entry
            for patterns in args
            for entry in ([patterns] if isinstance(patterns, str) else patterns)
        )
        self.entrypoint_spec = PathSpec.from_lines("gitwildmatch", self.entrypoint)

    @rule(AstRoot)
    @internal
    def root(self, node: AstRoot) -> Optional[AstRoot]:
        compilation_unit, module = self.modules.match_ast(node)

        if (
            isinstance(node, AstModuleRoot)
            and not module.executed
            and module.resource_location
            and not self.entrypoint_spec.match_file(module.resource_location)
        ):
            module.execution_hooks.append(
                partial(
                    self.restore_module,
                    self.modules.database.current,
                    node,
                    self.modules.database.step,
                )
            )
            return None

        with self.modules.error_handler(
            "Top-level statement raised an exception.", module.resource_location
        ):
            node = self.modules.eval(module)
            compilation_unit.priority = module.execution_index
            return node

    def restore_module(self, key: TextFileBase[Any], node: AstModuleRoot, step: int):
        compilation_unit = self.modules.database[key]
        compilation_unit.ast = node
        self.modules.database.enqueue(key, step, compilation_unit.priority)


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
