__all__ = [
    "Mecha",
    "MechaOptions",
    "AstCacheBackend",
    "FORMATTING_PRESETS",
]


import csv
import logging
import os
import pickle
import sys
from contextlib import contextmanager
from dataclasses import InitVar, dataclass
from io import BufferedReader, BufferedWriter
from pathlib import Path
from time import perf_counter_ns
from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

from beet import (
    LATEST_MINECRAFT_VERSION,
    Cache,
    Context,
    DataPack,
    Function,
    NamespaceFile,
    TextFileBase,
)
from beet.core.utils import (
    FileSystemPath,
    JsonDict,
    VersionNumber,
    extra_field,
    import_from_string,
)
from pydantic import BaseModel, validator
from tokenstream import InvalidSyntax, Preprocessor, TokenStream, set_location

from .ast import AstLiteral, AstNode, AstRoot
from .config import CommandTree
from .database import CompilationDatabase, CompilationUnit
from .diagnostic import (
    Diagnostic,
    DiagnosticCollection,
    DiagnosticError,
    DiagnosticErrorSummary,
)
from .dispatch import Dispatcher, MutatingReducer, Reducer
from .parse import delegate, get_parsers
from .preprocess import wrap_backslash_continuation
from .serialize import FormattingOptions, Serializer
from .spec import CommandSpec

AstNodeType = TypeVar("AstNodeType", bound=AstNode)
TextFileType = TypeVar("TextFileType", bound=TextFileBase[Any])


logger = logging.getLogger("mecha")


@dataclass
class AstCacheBackend:
    """Backend for the ast cache."""

    version: str = import_from_string("mecha.__version__")

    def load_data(self, f: BufferedReader) -> JsonDict:
        """Load the pickled data."""
        data = pickle.load(f)
        if data["mecha"] != self.version or data["python"] != sys.version:
            raise ValueError("Version mismatch.")
        return data

    def dump_data(self, data: JsonDict, f: BufferedWriter):
        """Dump the pickled data."""
        data["mecha"] = self.version
        data["python"] = sys.version
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

    def load(self, f: BufferedReader) -> AstRoot:
        """Load the ast."""
        return self.load_data(f)["ast"]

    def dump(self, node: AstRoot, f: BufferedWriter):
        """Dump the ast."""
        self.dump_data({"ast": node}, f)


FORMATTING_PRESETS: Dict[str, JsonDict] = {
    "minify": {
        "layout": "dense",
        "cmd_compact": True,
        "nbt_compact": True,
        "json_compact": True,
    },
    "dense": {
        "layout": "dense",
    },
    "preserve": {
        "layout": "preserve",
    },
}


class MechaOptions(BaseModel):
    """Mecha options."""

    version: str = ""
    multiline: bool = False
    formatting: FormattingOptions = FormattingOptions()
    readonly: Optional[bool] = None
    match: Optional[List[str]] = None
    rules: Dict[str, Literal["ignore", "info", "warn", "error"]] = {}
    cache: bool = True
    output_perf: Optional[FileSystemPath] = None

    @validator("formatting", pre=True)
    def formatting_preset(cls, value: Any):
        if isinstance(value, str):
            assert value in FORMATTING_PRESETS, "invalid formatting preset"
            return FORMATTING_PRESETS[value]
        return value


@dataclass
class Mecha:
    """Class exposing the command api."""

    ctx: InitVar[Optional[Context]] = None
    version: InitVar[VersionNumber] = LATEST_MINECRAFT_VERSION
    multiline: InitVar[bool] = False
    formatting: InitVar[Optional[FormattingOptions]] = None
    readonly: bool = False
    match: Optional[List[str]] = None

    directory: Path = extra_field(init=False)
    cache: Optional[Cache] = extra_field(default=None)
    cache_backend: AstCacheBackend = extra_field(default_factory=AstCacheBackend)
    output_perf: Optional[FileSystemPath] = extra_field(default=None)
    perf_report: Optional[List[Tuple[str, str, int, List[float]]]] = extra_field(
        default=None
    )

    spec: CommandSpec = extra_field(default=None)

    providers: List[Type[NamespaceFile]] = extra_field(
        default_factory=lambda: [Function]
    )

    preprocessor: Preprocessor = extra_field(default=wrap_backslash_continuation)

    lint: Dispatcher[AstRoot] = extra_field(init=False)
    transform: Dispatcher[AstRoot] = extra_field(init=False)
    optimize: Dispatcher[AstRoot] = extra_field(init=False)
    check: Dispatcher[AstRoot] = extra_field(init=False)

    steps: List[Dispatcher[AstRoot]] = extra_field(default_factory=list)

    serialize: Serializer = extra_field(init=False)

    database: CompilationDatabase = extra_field(default_factory=CompilationDatabase)
    diagnostics: DiagnosticCollection = extra_field(
        default_factory=DiagnosticCollection
    )

    def __post_init__(
        self,
        ctx: Optional[Context],
        version: VersionNumber,
        multiline: bool,
        formatting: Optional[FormattingOptions],
    ):
        if ctx:
            opts = ctx.validate("mecha", MechaOptions)
            version = opts.version or ctx.minecraft_version
            multiline = opts.multiline
            formatting = opts.formatting

            if opts.readonly is not None:
                self.readonly = opts.readonly
            if opts.match is not None:
                self.match = opts.match

            self.directory = ctx.directory

            self.lint = Reducer(levels=opts.rules)
            self.transform = MutatingReducer(levels=opts.rules)
            self.optimize = MutatingReducer(levels=opts.rules)
            self.check = Reducer(levels=opts.rules)

            if not self.cache and opts.cache:
                self.cache = ctx.cache["mecha"]

            if opts.output_perf:
                self.output_perf = ctx.directory / opts.output_perf

            ctx.require(self.finalize)

        else:
            self.directory = Path.cwd()

            self.lint = Reducer()
            self.transform = MutatingReducer()
            self.optimize = MutatingReducer()
            self.check = Reducer()

        self.steps.append(self.lint)
        self.steps.append(self.transform)
        self.steps.append(self.optimize)
        self.steps.append(self.check)

        if self.perf_report is None and self.output_perf:
            self.perf_report = []

        if not self.spec:
            self.spec = CommandSpec(
                multiline=multiline,
                tree=CommandTree.load_from(version=version),
                parsers=get_parsers(version),
            )

        self.serialize = Serializer(
            spec=self.spec,
            database=self.database,
            formatting=formatting or FormattingOptions(),
        )

    @contextmanager
    def prepare_token_stream(
        self,
        stream: TokenStream,
        multiline: Optional[bool] = None,
    ) -> Iterator[TokenStream]:
        """Prepare the token stream for parsing."""
        with stream.reset(*stream.data), stream.provide(
            spec=self.spec,
            multiline=self.spec.multiline if multiline is None else multiline,
        ):
            with stream.reset_syntax(comment=r"#.*$", literal=AstLiteral.regex.pattern):
                with stream.indent(skip=["comment"]), stream.ignore("indent", "dedent"):
                    with stream.intercept("newline", "eof"):
                        yield stream

    @overload
    def parse(
        self,
        source: Union[TextFileBase[Any], List[str], str],
        *,
        filename: Optional[FileSystemPath] = None,
        resource_location: Optional[str] = None,
        multiline: Optional[bool] = None,
        provide: Optional[JsonDict] = None,
        preprocessor: Optional[Preprocessor] = None,
    ) -> AstRoot:
        ...

    @overload
    def parse(
        self,
        source: Union[TextFileBase[Any], List[str], str],
        *,
        type: Type[AstNodeType],
        filename: Optional[FileSystemPath] = None,
        resource_location: Optional[str] = None,
        multiline: Optional[bool] = None,
        provide: Optional[JsonDict] = None,
        preprocessor: Optional[Preprocessor] = None,
    ) -> AstNodeType:
        ...

    @overload
    def parse(
        self,
        source: Union[TextFileBase[Any], List[str], str],
        *,
        using: str,
        filename: Optional[FileSystemPath] = None,
        resource_location: Optional[str] = None,
        multiline: Optional[bool] = None,
        provide: Optional[JsonDict] = None,
        preprocessor: Optional[Preprocessor] = None,
    ) -> Any:
        ...

    def parse(
        self,
        source: Union[TextFileBase[Any], List[str], str],
        *,
        type: Optional[Type[AstNode]] = None,
        using: Optional[str] = None,
        filename: Optional[FileSystemPath] = None,
        resource_location: Optional[str] = None,
        multiline: Optional[bool] = None,
        provide: Optional[JsonDict] = None,
        preprocessor: Optional[Preprocessor] = None,
    ) -> Any:
        """Parse the given source into an AST."""
        if using:
            parser = using
        else:
            if not type:
                type = AstRoot
            if not type.parser:
                raise TypeError(f"No parser directly associated with {type}.")
            parser = type.parser

        if isinstance(source, (list, str)):
            source = Function(source)

        if not filename and source.source_path:
            filename = os.path.relpath(source.source_path, self.directory)

        cache_miss = None

        if self.cache and filename:
            ast_path = self.cache.get_path(f"{self.directory / filename}-ast")

            if not self.cache.has_changed(self.directory / filename):
                try:
                    with ast_path.open("rb") as f:
                        ast = self.cache_backend.load(f)
                        logger.debug('Load cached ast for file "%s".', filename)
                        return ast
                except Exception:
                    pass

            cache_miss = ast_path

        stream = TokenStream(
            source.text,
            preprocessor=preprocessor or self.preprocessor,
        )

        try:
            with self.prepare_token_stream(stream, multiline=multiline):
                with stream.provide(**provide or {}):
                    ast = delegate(parser, stream)
        except InvalidSyntax as exc:
            if self.cache and filename and cache_miss:
                self.cache.invalidate_changes(self.directory / filename)
            d = Diagnostic(
                level="error",
                message=str(exc),
                notes=exc.notes,
                hint=resource_location,
                filename=str(filename) if filename else None,
                file=source,
            )
            raise DiagnosticError(DiagnosticCollection([set_location(d, exc)])) from exc
        else:
            if self.cache and filename and cache_miss:
                try:
                    with cache_miss.open("wb") as f:
                        self.cache_backend.dump(ast, f)
                        logger.debug('Update cached ast for file "%s".', filename)
                except Exception:
                    pass
            return ast

    @overload
    def compile(
        self,
        source: DataPack,
        *,
        match: Optional[List[str]] = None,
        multiline: Optional[bool] = None,
        formatting: Optional[JsonDict] = None,
        readonly: Optional[bool] = None,
        initial_step: int = 0,
        report: Optional[DiagnosticCollection] = None,
    ) -> DataPack:
        ...

    @overload
    def compile(
        self,
        source: TextFileType,
        *,
        filename: Optional[FileSystemPath] = None,
        resource_location: Optional[str] = None,
        multiline: Optional[bool] = None,
        formatting: Optional[JsonDict] = None,
        readonly: Optional[bool] = None,
        initial_step: int = 0,
        report: Optional[DiagnosticCollection] = None,
    ) -> TextFileType:
        ...

    @overload
    def compile(
        self,
        source: Union[List[str], str, AstRoot],
        *,
        filename: Optional[FileSystemPath] = None,
        resource_location: Optional[str] = None,
        multiline: Optional[bool] = None,
        formatting: Optional[JsonDict] = None,
        readonly: Optional[bool] = None,
        initial_step: int = 0,
        report: Optional[DiagnosticCollection] = None,
    ) -> Function:
        ...

    def compile(
        self,
        source: Union[DataPack, TextFileBase[Any], List[str], str, AstRoot],
        *,
        match: Optional[List[str]] = None,
        filename: Optional[FileSystemPath] = None,
        resource_location: Optional[str] = None,
        multiline: Optional[bool] = None,
        formatting: Optional[JsonDict] = None,
        readonly: Optional[bool] = None,
        initial_step: int = 0,
        report: Optional[DiagnosticCollection] = None,
    ) -> Union[DataPack, TextFileBase[Any]]:
        """Apply all compilation steps."""
        self.database.setup_compilation()

        if formatting is None:
            formatting = {}
        if readonly is None:
            readonly = self.readonly

        if isinstance(source, DataPack):
            result = source

            if match is None:
                match = self.match

            for file_type in self.providers:
                if not issubclass(file_type, TextFileBase):
                    continue
                for key in source[file_type].match(*match or ["*"]):
                    value = source[file_type][key]
                    self.database[value] = CompilationUnit(
                        resource_location=key,
                        filename=(
                            os.path.relpath(value.source_path, self.directory)
                            if value.source_path
                            else None
                        ),
                    )
                    self.database.enqueue(value)
        else:
            if isinstance(source, (list, str)):
                source = Function(source)

            if isinstance(source, TextFileBase):
                result = source
                if not filename and source.source_path:
                    filename = os.path.relpath(source.source_path, self.directory)
            else:
                result = Function()

            self.database[result] = CompilationUnit(
                ast=source if isinstance(source, AstRoot) else None,
                resource_location=resource_location,
                filename=str(filename) if filename else None,
            )
            self.database.enqueue(result)

        for step, function in self.database.process_queue():
            compilation_unit = self.database[function]
            start_time = perf_counter_ns()

            if step < 0:
                if compilation_unit.ast:
                    self.database.enqueue(function, initial_step)
                    continue
                try:
                    compilation_unit.source = function.text
                    compilation_unit.ast = self.parse(
                        function,
                        filename=compilation_unit.filename,
                        resource_location=compilation_unit.resource_location,
                        multiline=multiline,
                    )
                    self.database.enqueue(function, initial_step)
                except DiagnosticError as exc:
                    compilation_unit.diagnostics.extend(exc.diagnostics)

            elif step < len(self.steps):
                if not compilation_unit.ast:
                    continue
                with self.steps[step].use_diagnostics(compilation_unit.diagnostics):
                    if ast := self.steps[step](compilation_unit.ast):
                        if not compilation_unit.diagnostics.error:
                            compilation_unit.ast = ast
                            self.database.enqueue(
                                key=function,
                                step=step + 1,
                                priority=compilation_unit.priority,
                            )

            elif not readonly:
                if not compilation_unit.ast:
                    continue
                with self.serialize.use_diagnostics(compilation_unit.diagnostics):
                    function.text = self.serialize(compilation_unit.ast, **formatting)

            compilation_unit.perf[step] = (perf_counter_ns() - start_time) * 1e-06

        sorted_functions = sorted(
            self.database.session,
            key=lambda f: self.database[f].resource_location or "<unknown>",
        )

        if self.perf_report is not None:
            for function in sorted_functions:
                compilation_unit = self.database[function]
                self.perf_report.append(
                    (
                        compilation_unit.filename or "",
                        compilation_unit.resource_location or "",
                        len(list(compilation_unit.diagnostics.get_all_errors())),
                        [
                            compilation_unit.perf.get(i, float("nan"))
                            for i in range(-1, len(self.steps) + 1)
                        ],
                    )
                )

        diagnostics = DiagnosticCollection(
            [
                exc
                for function in sorted_functions
                for exc in self.database[function].diagnostics.exceptions
            ]
        )

        if report:
            report.extend(diagnostics)
        else:
            if errors := list(diagnostics.get_all_errors()):
                raise DiagnosticError(DiagnosticCollection(errors))

        return result

    def log_reported_diagnostics(self):
        """Log reported diagnostics."""
        for diagnostic in self.diagnostics.exceptions:
            message = diagnostic.format_message()

            if diagnostic.file:
                if source := self.database[diagnostic.file].source:
                    if code := diagnostic.format_code(source):
                        message += f"\n{code}"

            if diagnostic.notes:
                message += f"\n{diagnostic.format_notes()}"

            extra = {"annotate": diagnostic.format_location()}

            if diagnostic.level == "error":
                logger.error("%s", message, extra=extra)
            elif diagnostic.level == "warn":
                logger.warning("%s", message, extra=extra)
            elif diagnostic.level == "info":
                logger.info("%s", message, extra=extra)

    def format_perf(self) -> List[List[str]]:
        """Format perf report."""
        step_headers = [
            "Lint"
            if step is self.lint
            else "Transform"
            if step is self.transform
            else "Optimize"
            if step is self.optimize
            else "Check"
            if step is self.check
            else repr(step)
            for step in self.steps
        ]

        return [
            ["Filename", "Resource location", "Errors", "Parse"]
            + step_headers
            + ["Serialize"]
        ] + [
            [filename, resource_location, str(errors)] + [f"{t:.3f}" for t in steps]
            for filename, resource_location, errors, steps in self.perf_report or []
        ]

    def finalize(self, ctx: Context):
        """Plugin that logs diagnostics and raises an exception if there are errors."""
        try:
            yield
        except:
            raise
        else:
            if errors := list(self.diagnostics.get_all_errors()):
                raise DiagnosticErrorSummary(DiagnosticCollection(errors))
        finally:
            if path := self.output_perf:
                logger.info('Output perf "%s".', os.path.relpath(path, self.directory))
                with open(path, "w") as f:
                    csv.writer(f).writerows(self.format_perf())
            self.log_reported_diagnostics()
