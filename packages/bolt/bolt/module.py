__all__ = [
    "Module",
    "CompiledModule",
    "ModuleManager",
    "ModuleCacheBackend",
    "MacroLibrary",
    "CodegenResult",
    "UnusableCompilationUnit",
    "SilentCompilationInterrupt",
]


import logging
import marshal
from contextlib import contextmanager
from dataclasses import dataclass, field
from io import BufferedReader, BufferedWriter
from pathlib import Path
from types import CodeType
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Iterator,
    List,
    Mapping,
    Optional,
    Protocol,
    Set,
    Tuple,
    Union,
    cast,
)

from beet import BubbleException, Cache, TextFile, TextFileBase
from beet.core.utils import JsonDict, extra_field, import_from_string, required_field
from mecha import (
    AstCacheBackend,
    AstRoot,
    CompilationDatabase,
    CompilationError,
    CompilationUnit,
    DiagnosticCollection,
    DiagnosticError,
    Dispatcher,
    MechaError,
)
from tokenstream import InvalidSyntax

from .ast import AstMacro
from .utils import internal, rewrite_traceback

logger = logging.getLogger("mecha")


class UnusableCompilationUnit(MechaError):
    """Raised when a compilation unit can not be used to instantiate a module."""

    message: str
    compilation_unit: CompilationUnit

    def __init__(self, message: str, compilation_unit: CompilationUnit) -> None:
        super().__init__(message, compilation_unit)
        self.message = message
        self.compilation_unit = compilation_unit

    def __str__(self) -> str:
        return self.message


class SilentCompilationInterrupt(DiagnosticCollection):
    """Raised for interrupting the compilation when an unusable compilation unit already reported its own diagnostics."""


class Module(TextFile):
    """Class representing a bolt module."""

    scope: ClassVar[Tuple[str, ...]] = ("modules",)
    extension: ClassVar[str] = ".bolt"


MacroLibrary = Dict[str, Dict[Tuple[str, AstMacro], Optional[Tuple[str, str]]]]


@dataclass
class CompiledModule:
    """Class holding the state of a compiled module."""

    ast: AstRoot
    code: Optional[CodeType]
    refs: List[Any]
    macros: MacroLibrary
    output: Optional[str]
    resource_location: Optional[str]
    globals: Set[str]
    namespace: JsonDict = field(default_factory=dict)
    executing: bool = False
    executed: bool = False
    execution_hooks: List[Callable[[], Any]] = field(default_factory=list)
    execution_index: int = 0


@dataclass(frozen=True)
class CodegenResult:
    source: Optional[str] = None
    output: Optional[str] = None
    refs: List[Any] = field(default_factory=list)
    macros: MacroLibrary = field(default_factory=dict)


class ModuleParseCallback(Protocol):
    """Callback required by the module manager for parsing."""

    def __call__(
        self,
        source: TextFileBase[Any],
        *,
        filename: Optional[str],
        resource_location: Optional[str],
    ) -> AstRoot:
        ...


@dataclass
class ModuleManager(Mapping[TextFileBase[Any], CompiledModule]):
    """Container for managing bolt modules."""

    directory: Path = extra_field()
    database: CompilationDatabase = extra_field()
    codegen: Dispatcher[CodegenResult] = extra_field()
    parse_callback: ModuleParseCallback = extra_field()
    cache: Optional[Cache] = extra_field(default=None)

    registry: Dict[TextFileBase[Any], CompiledModule] = extra_field(
        default_factory=dict
    )
    stack: List[CompiledModule] = extra_field(default_factory=list)
    parse_stack: List[TextFileBase[Any]] = extra_field(default_factory=list)
    globals: JsonDict = extra_field(default_factory=dict)
    builtins: Set[str] = extra_field(default_factory=set)

    execution_count: int = 0

    @property
    def current(self) -> CompiledModule:
        """Return the currently executing module."""
        if not self.stack:
            raise ValueError("No module currently executing.")
        return self.stack[-1]

    @property
    def current_path(self) -> str:
        """Return the path corresponding to the currently executing module."""
        if path := self.current.resource_location:
            return path
        raise ValueError(
            "Currently executing module has no associated resource location."
        )

    def match_ast(
        self,
        node: AstRoot,
        current: Optional[Union[TextFileBase[Any], str]] = None,
    ) -> Tuple[CompilationUnit, CompiledModule]:
        """Return the compilation unit and executable module for the current ast."""
        if not current:
            current = self.database.current
        elif isinstance(current, str):
            current = self.database.index[current]

        compilation_unit = self.database[current]
        compilation_unit.ast = node

        return compilation_unit, self[current]

    def __getitem__(self, current: Union[TextFileBase[Any], str]) -> CompiledModule:
        if isinstance(current, str):
            current = self.database.index[current]

        compilation_unit = self.database[current]
        name = compilation_unit.resource_location or "<unknown>"

        if module := self.registry.get(current):
            if (
                module.executed
                or not compilation_unit.ast
                or module.ast is compilation_unit.ast
            ):
                return module
            logger.warning('Code generation due to ast update for module "%s".', name)

        elif not compilation_unit.ast:
            previous = self.database.current
            self.database.current = current
            try:
                compilation_unit.ast = self.parse_callback(
                    current,
                    filename=compilation_unit.filename,
                    resource_location=compilation_unit.resource_location,
                )
            except DiagnosticError as exc:
                raise UnusableCompilationUnit(
                    "Parsing failed.", compilation_unit
                ) from exc
            finally:
                self.database.current = previous
            return self[current]

        else:
            logger.debug('Code generation for module "%s".', name)

        result = self.codegen(compilation_unit.ast)

        if result.source and result.output:
            code = compile(
                source=result.source,
                filename=(
                    str(self.directory / compilation_unit.filename)
                    if compilation_unit.filename
                    else name
                ),
                mode="exec",
            )

        else:
            code = None

        module = CompiledModule(
            ast=compilation_unit.ast,
            code=code,
            refs=result.refs,
            macros=result.macros,
            output=result.output,
            resource_location=compilation_unit.resource_location,
            globals=set(self.globals),
        )
        self.registry[current] = module

        return module

    def __iter__(self) -> Iterator[TextFileBase[Any]]:
        return iter(self.database)

    def __len__(self) -> int:
        return len(self.database)

    def get(self, current: Union[TextFileBase[Any], str]) -> Optional[CompiledModule]:
        """Return executable module if exists."""
        if isinstance(current, str):
            if current not in self.database.index:
                return None
            current = self.database.index[current]

        if current not in self.database:
            return None

        return self[current]

    @internal
    def eval(self, module: CompiledModule) -> AstRoot:
        """Run the module and return the output ast."""
        if not module.executed:
            module.executed = True
            for hook in module.execution_hooks:
                hook()

        if not module.code or not module.output:
            return module.ast
        if module.output in module.namespace:
            return module.namespace[module.output]

        if module.executing:
            raise ValueError("Import cycle detected.")

        logger.debug('Evaluate module "%s".', module.resource_location or "<unknown>")

        module.namespace.update(self.globals)
        module.namespace["_bolt_refs"] = module.refs
        module.namespace["__name__"] = module.resource_location
        module.namespace["__file__"] = module.code.co_filename

        self.stack.append(module)
        module.executing = True

        try:
            exec(module.code, module.namespace)
        finally:
            module.executing = False
            self.stack.pop()
            self.execution_count += 1
            module.execution_index = self.execution_count

        return module.namespace[module.output]

    @contextmanager
    @internal
    def error_handler(self, message: str, resource_location: Optional[str] = None):
        """Error handler for running module code."""
        try:
            yield
        except (BubbleException, InvalidSyntax, SilentCompilationInterrupt):
            raise
        except UnusableCompilationUnit as exc:
            if not exc.compilation_unit.diagnostics.error:
                message = "Failed to instantiate module."
                if resource_location:
                    message += f" ({resource_location})"
                raise CompilationError(message) from rewrite_traceback(exc)
            raise SilentCompilationInterrupt() from None
        except Exception as exc:
            if resource_location:
                message += f" ({resource_location})"
            raise CompilationError(message) from rewrite_traceback(exc)

    @contextmanager
    def parse_push(self, current: TextFileBase[Any]):
        """Push the current file onto the parse stack."""
        if current in self.parse_stack:
            stack = " -> ".join(
                f'"{self.database[entry].resource_location or "<unknown>"}"'
                for entry in self.parse_stack + [current]
            )
            raise UnusableCompilationUnit(
                f"Cyclic parsing dependency {stack}.",
                compilation_unit=self.database[current],
            )

        self.parse_stack.append(current)

        try:
            yield
        finally:
            self.parse_stack.pop()


@dataclass
class ModuleCacheBackend(AstCacheBackend):
    """Cache backend that also restores the generated modules."""

    bolt_version: str = import_from_string("bolt.__version__")

    modules: ModuleManager = required_field(repr=False, hash=False, compare=False)

    def load_data(self, f: BufferedReader) -> JsonDict:
        data = super().load_data(f)

        if data["bolt"] != self.bolt_version:
            raise ValueError("Version mismatch.")
        if data["globals"] != set(self.modules.globals):
            raise ValueError("Globals mismatch.")

        for group, exports in cast(MacroLibrary, data["macros"]).items():
            for (_, macro), extern in exports.items():
                if extern:
                    resource_location, name = extern
                    macros = self.modules[resource_location].macros
                    if group not in macros or (name, macro) not in macros[group]:
                        raise ValueError("Macro mismatch.")

        return data

    def dump_data(self, data: JsonDict, f: BufferedWriter):
        data["bolt"] = self.bolt_version
        super().dump_data(data, f)

    def load(self, f: BufferedReader) -> AstRoot:
        data = self.load_data(f)

        self.modules.registry[self.modules.database.current] = CompiledModule(
            ast=data["ast"],
            code=marshal.load(f),
            refs=data["refs"],
            macros=data["macros"],
            output=data["output"],
            resource_location=data["resource_location"],
            globals=data["globals"],
        )

        return data["ast"]

    def dump(self, node: AstRoot, f: BufferedWriter):
        _, module = self.modules.match_ast(node)

        self.dump_data(
            {
                "ast": module.ast,
                "refs": module.refs,
                "macros": module.macros,
                "output": module.output,
                "resource_location": module.resource_location,
                "globals": module.globals,
            },
            f,
        )

        marshal.dump(module.code, f)
