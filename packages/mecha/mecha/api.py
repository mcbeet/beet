__all__ = [
    "Mecha",
    "MechaOptions",
    "AstCacheBackend",
]


import logging
import os
import pickle
import sys
from contextlib import contextmanager
from dataclasses import InitVar, dataclass
from io import BufferedReader, BufferedWriter
from pathlib import Path
from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Literal,
    Optional,
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
from pydantic import BaseModel
from tokenstream import InvalidSyntax, TokenStream
from tokenstream.location import set_location

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
from .serialize import Formatting, Serializer
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
        pickle.dump(data, f)

    def load(self, f: BufferedReader) -> AstRoot:
        """Load the ast."""
        return self.load_data(f)["ast"]

    def dump(self, node: AstRoot, f: BufferedWriter):
        """Dump the ast."""
        self.dump_data({"ast": node}, f)


class MechaOptions(BaseModel):
    """Mecha options."""

    version: str = ""
    multiline: bool = False
    formatting: Formatting = "dense"
    readonly: Optional[bool] = None
    match: Optional[List[str]] = None
    rules: Dict[str, Literal["ignore", "info", "warn", "error"]] = {}
    cache: bool = True


@dataclass
class Mecha:
    """Class exposing the command api."""

    ctx: InitVar[Optional[Context]] = None
    version: InitVar[VersionNumber] = LATEST_MINECRAFT_VERSION
    multiline: InitVar[bool] = False
    formatting: InitVar[Formatting] = "dense"
    readonly: bool = False
    match: Optional[List[str]] = None

    directory: Path = extra_field(init=False)
    cache: Optional[Cache] = extra_field(default=None)
    cache_backend: AstCacheBackend = extra_field(default_factory=AstCacheBackend)

    spec: CommandSpec = extra_field(default=None)

    providers: List[Type[NamespaceFile]] = extra_field(
        default_factory=lambda: [Function]
    )

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
        formatting: Formatting,
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

        if not self.spec:
            self.spec = CommandSpec(
                multiline=multiline,
                tree=CommandTree.load_from(version=version),
                parsers=get_parsers(version),
            )

        self.serialize = Serializer(
            spec=self.spec,
            database=self.database,
            formatting=formatting,
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

        stream = TokenStream(source.text)

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
        formatting: Optional[Formatting] = None,
        readonly: Optional[bool] = None,
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
        formatting: Optional[Formatting] = None,
        readonly: Optional[bool] = None,
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
        formatting: Optional[Formatting] = None,
        readonly: Optional[bool] = None,
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
        formatting: Optional[Formatting] = None,
        readonly: Optional[bool] = None,
        report: Optional[DiagnosticCollection] = None,
    ) -> Union[DataPack, TextFileBase[Any]]:
        """Apply all compilation steps."""
        self.database.setup_compilation()

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

            if step < 0:
                if compilation_unit.ast:
                    self.database.enqueue(function, 0)
                    continue
                try:
                    compilation_unit.source = function.text
                    compilation_unit.ast = self.parse(
                        function,
                        filename=compilation_unit.filename,
                        resource_location=compilation_unit.resource_location,
                        multiline=multiline,
                    )
                    self.database.enqueue(function, 0)
                except DiagnosticError as exc:
                    compilation_unit.diagnostics.extend(exc.diagnostics)

            elif step < len(self.steps):
                if not compilation_unit.ast:
                    continue
                with self.steps[step].use_diagnostics(compilation_unit.diagnostics):
                    compilation_unit.ast = self.steps[step](compilation_unit.ast)
                    if compilation_unit.ast:
                        self.database.enqueue(function, step + 1)

            elif not readonly:
                if not compilation_unit.ast:
                    continue
                with self.serialize.use_diagnostics(compilation_unit.diagnostics):
                    function.text = self.serialize(compilation_unit.ast, formatting)

        diagnostics = DiagnosticCollection(
            [
                exc
                for function in sorted(
                    self.database.session,
                    key=lambda f: self.database[f].resource_location or "<unknown>",
                )
                for exc in self.database[function].diagnostics.exceptions
            ]
        )

        if report:
            report.extend(diagnostics)
        else:
            if errors := list(diagnostics.get_all_errors()):
                raise DiagnosticError(DiagnosticCollection(errors))

        return result

    def finalize(self, ctx: Context):
        """Plugin that logs diagnostics and raises an exception if there are errors."""
        yield

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

        if errors := list(self.diagnostics.get_all_errors()):
            raise DiagnosticErrorSummary(DiagnosticCollection(errors))
