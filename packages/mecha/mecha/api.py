__all__ = [
    "Mecha",
    "MechaOptions",
]


import os
from contextlib import contextmanager
from dataclasses import InitVar, dataclass
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

from beet import Context, DataPack, Function, TextFileBase
from beet.core.utils import FileSystemPath, JsonDict, extra_field
from pydantic import BaseModel
from tokenstream import InvalidSyntax, TokenStream
from tokenstream.location import set_location

from .ast import AstNode, AstRoot
from .config import CommandTree
from .diagnostic import Diagnostic, DiagnosticCollection, DiagnosticError
from .dispatch import Dispatcher, MutatingReducer, Reducer
from .parse import delegate, get_default_parsers
from .serialize import Serializer
from .spec import CommandSpec

AstNodeType = TypeVar("AstNodeType", bound=AstNode)
TextFileType = TypeVar("TextFileType", bound=TextFileBase[Any])


class MechaOptions(BaseModel):
    """Mecha options."""

    version: str = "1.17"
    multiline: bool = False
    rules: Dict[str, Literal["ignore", "info", "warn", "error"]] = {}


@dataclass
class Mecha:
    """Class exposing the command api."""

    ctx: InitVar[Optional[Context]] = None
    version: InitVar[str] = "1.17"
    multiline: InitVar[bool] = False

    directory: Path = extra_field(init=False)

    spec: CommandSpec = extra_field(default=None)

    lint: Dispatcher[AstNode] = extra_field(init=False)
    normalize: Dispatcher[AstNode] = extra_field(init=False)
    transform: Dispatcher[AstNode] = extra_field(init=False)
    optimize: Dispatcher[AstNode] = extra_field(init=False)
    check: Dispatcher[AstNode] = extra_field(init=False)

    steps: List[Dispatcher[AstNode]] = extra_field(default_factory=list)

    serialize: Dispatcher[str] = extra_field(init=False)
    diagnostics: DiagnosticCollection = extra_field(init=False)

    def __post_init__(self, ctx: Optional[Context], version: str, multiline: bool):
        if ctx:
            opts = ctx.validate("mecha", MechaOptions)
            version = opts.version
            multiline = opts.multiline

            self.directory = ctx.directory

            self.lint = Reducer(levels=opts.rules)
            self.normalize = MutatingReducer(levels=opts.rules)
            self.transform = MutatingReducer(levels=opts.rules)
            self.optimize = MutatingReducer(levels=opts.rules)
            self.check = Reducer(levels=opts.rules)

        else:
            self.directory = Path.cwd()

            self.lint = Reducer()
            self.normalize = MutatingReducer()
            self.transform = MutatingReducer()
            self.optimize = MutatingReducer()
            self.check = Reducer()

        self.steps.append(self.lint)
        self.steps.append(self.normalize)
        self.steps.append(self.transform)
        self.steps.append(self.optimize)
        self.steps.append(self.check)

        if not self.spec:
            self.spec = CommandSpec(
                multiline=multiline,
                tree=CommandTree.load_from(version=version),
                parsers=get_default_parsers(),
            )

        self.serialize = Serializer(self.spec)
        self.diagnostics = DiagnosticCollection()

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
            with stream.reset_syntax(comment=r"#.*$", literal=r"\S+"):
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

        stream = TokenStream(source.text)

        try:
            with self.prepare_token_stream(stream, multiline=multiline):
                with stream.provide(**provide or {}):
                    return delegate(parser, stream)
        except InvalidSyntax as exc:
            d = Diagnostic(
                level="error",
                message=str(exc),
                hint=resource_location,
                filename=str(filename) if filename else None,
            )
            raise DiagnosticError(DiagnosticCollection([set_location(d, exc)])) from exc

    @overload
    def compile(
        self,
        source: DataPack,
        *,
        multiline: Optional[bool] = None,
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
        report: Optional[DiagnosticCollection] = None,
    ) -> TextFileType:
        ...

    @overload
    def compile(
        self,
        source: Union[List[str], str, AstNode],
        *,
        filename: Optional[FileSystemPath] = None,
        resource_location: Optional[str] = None,
        multiline: Optional[bool] = None,
        report: Optional[DiagnosticCollection] = None,
    ) -> Function:
        ...

    def compile(
        self,
        source: Union[DataPack, TextFileBase[Any], List[str], str, AstNode],
        *,
        filename: Optional[FileSystemPath] = None,
        resource_location: Optional[str] = None,
        multiline: Optional[bool] = None,
        report: Optional[DiagnosticCollection] = None,
    ) -> Union[DataPack, TextFileBase[Any]]:
        if not filename and isinstance(source, TextFileBase) and source.source_path:
            filename = os.path.relpath(source.source_path, self.directory)

        diagnostics = DiagnosticCollection(
            hint=resource_location,
            filename=str(filename) if filename else None,
        )

        if isinstance(source, DataPack):
            result = source

            for path, function in list(source.functions.items()):
                self.compile(
                    function,
                    resource_location=path,
                    multiline=multiline,
                    report=diagnostics,
                )

        else:
            if isinstance(source, (list, str)):
                source = Function(source)
            if isinstance(source, TextFileBase):
                result = source
            else:
                result = Function()

            ast = None

            if isinstance(source, AstNode):
                ast = source
            else:
                try:
                    ast = self.parse(
                        source,
                        filename=filename,
                        resource_location=resource_location,
                        multiline=multiline,
                    )
                except DiagnosticError as exc:
                    diagnostics.extend(exc.diagnostics)

            if ast:
                for compiler_pass in self.steps:
                    with compiler_pass.use_diagnostics(diagnostics):
                        ast = compiler_pass(ast)

                with self.serialize.use_diagnostics(diagnostics):
                    result.text = self.serialize(ast)

        if report:
            report.extend(diagnostics)
        else:
            if errors := list(diagnostics.get_all_errors()):
                raise DiagnosticError(DiagnosticCollection(errors))

        return result
