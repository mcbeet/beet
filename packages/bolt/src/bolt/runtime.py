__all__ = [
    "Runtime",
    "Evaluator",
    "NonFunctionSerializer",
]


import builtins
from dataclasses import dataclass, field
from functools import partial
from importlib.resources import files
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Union

from beet import Context, TextFileBase, generate_tree
from beet.core.utils import JsonDict, extra_field, required_field
from mecha import (
    AstRoot,
    CommandSpec,
    CommandTree,
    CompilationDatabase,
    CompilationUnitProvider,
    Diagnostic,
    FileTypeCompilationUnitProvider,
    Mecha,
    Visitor,
    rule,
)
from mecha.contrib.nested_location import NestedLocationResolver
from mecha.contrib.relative_location import resolve_relative_location
from pathspec import PathSpec
from tokenstream import set_location

from .ast import AstNonFunctionRoot
from .codegen import Codegen
from .emit import CommandEmitter
from .helpers import get_bolt_helpers
from .loop_info import loop_info
from .memo import MemoHandler, MemoRegistry
from .module import (
    AssetModule,
    CompiledModule,
    Module,
    ModuleCacheBackend,
    ModuleManager,
)
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

    spec: CommandSpec
    module_provider: CompilationUnitProvider

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
                "mecha.contrib.nested_location",
                "mecha.contrib.nested_resources",
                "mecha.contrib.nested_yaml",
                "mecha.contrib.implicit_execute",
                self.finalize,
            )

            ctx.data.extend_namespace.append(Module)
            ctx.assets.extend_namespace.append(AssetModule)

            self.globals["ctx"] = ctx

            self.expose("generate_path", ctx.generate.path)
            self.expose("generate_id", ctx.generate.id)
            self.expose("generate_hash", ctx.generate.hash)
            self.expose("generate_objective", ctx.generate.objective)
            self.expose(
                "generate_tree",
                lambda *args, **kwargs: generate_tree(
                    (
                        root := (
                            kwargs.pop("root")
                            if "root" in kwargs
                            else self.get_nested_location()
                        )
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

        self.spec = mc.spec

        self.module_provider = FileTypeCompilationUnitProvider([Module, AssetModule])
        mc.providers.append(self.module_provider)

        commands_json = files("bolt.resources").joinpath("commands.json").read_text()
        command_tree = CommandTree.model_validate_json(commands_json)
        bolt_prototypes = set(CommandSpec(tree=command_tree).prototypes)
        mc.spec.add_commands(command_tree)
        mc.spec.parsers.update(
            get_bolt_parsers(mc.spec.parsers, self.modules, bolt_prototypes)
        )

        mc.steps.insert(0, self.evaluate)

        mc.serialize.extend(NonFunctionSerializer(database=mc.database))
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

    def get_nested_location(self) -> str:
        """Return the resource location associated with the current level of nesting."""
        root, relative_path = NestedLocationResolver.concat_nested_path(
            NestedLocationResolver.walk_location_hierarchy(
                self.spec, reversed(self.nesting)
            )
        )

        if not root:
            root = self.modules.current_path

        namespace, resolved = resolve_relative_location(
            relative_path,
            root,
            include_root_file=True,
        )
        return f"{namespace}:{resolved}"

    def finalize(self, ctx: Context):
        """Plugin that runs at the end of the build."""
        try:
            yield
        finally:
            for pack in [ctx.data, *ctx.data.overlays.values()]:
                pack[Module].clear()
            for pack in [ctx.assets, *ctx.assets.overlays.values()]:
                pack[AssetModule].clear()
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
            isinstance(self.modules.database.current, (Module, AssetModule))
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

    def restore_module(self, key: TextFileBase[Any], node: AstRoot, step: int):
        compilation_unit = self.modules.database[key]
        compilation_unit.ast = node
        self.modules.database.enqueue(key, step, compilation_unit.priority)


@dataclass
class NonFunctionSerializer(Visitor):
    """Serializer that preserves the original source of non-function files."""

    database: CompilationDatabase = required_field()

    @rule(AstNonFunctionRoot)
    def non_function_root(self, node: AstNonFunctionRoot, result: List[str]):
        if source := self.database[self.database.current].source:
            result.append(source)
        if node.commands:
            command = node.commands[0]
            name = command.identifier.partition(":")[0]
            d = Diagnostic(
                "warn", f'Ignored top-level "{name}" command outside function.'
            )
            return set_location(
                d, command, command.arguments[0] if command.arguments else command
            )
