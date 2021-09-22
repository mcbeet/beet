__all__ = [
    "Mecha",
    "MechaOptions",
]


from contextlib import contextmanager
from dataclasses import InitVar, dataclass
from typing import Any, Iterator, Optional, Type, TypeVar, Union, overload

from beet import Context, TextFile, TextFileBase
from beet.core.utils import JsonDict, extra_field
from pydantic import BaseModel
from tokenstream import TokenStream

from .ast import AstNode, AstRoot
from .config import CommandTree
from .dispatch import Dispatcher, MutatingReducer, Reducer
from .parse import delegate, get_default_parsers
from .serialize import Serializer
from .spec import CommandSpec

AstNodeType = TypeVar("AstNodeType", bound=AstNode)


class MechaOptions(BaseModel):
    """Mecha options."""

    version: str = "1.17"
    multiline: bool = False


@dataclass
class Mecha:
    """Class exposing the command api."""

    ctx: InitVar[Optional[Context]] = None
    version: InitVar[str] = "1.17"
    multiline: InitVar[bool] = False

    spec: CommandSpec = extra_field(default=None)

    normalize: Dispatcher[AstNode] = extra_field(init=False)
    transform: Dispatcher[AstNode] = extra_field(init=False)
    check: Dispatcher[AstNode] = extra_field(init=False)
    serialize: Dispatcher[str] = extra_field(init=False)

    def __post_init__(self, ctx: Optional[Context], version: str, multiline: bool):
        if ctx:
            opts = ctx.validate("mecha", MechaOptions)
            version = opts.version
            multiline = opts.multiline

        if not self.spec:
            self.spec = CommandSpec(
                multiline=multiline,
                tree=CommandTree.load_from(version=version),
                parsers=get_default_parsers(),
            )

        self.normalize = MutatingReducer()
        self.transform = MutatingReducer()
        self.check = Reducer()
        self.serialize = Serializer(self.spec)

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
        source: Union[TextFileBase[Any], str],
        *,
        filename: Optional[str] = None,
        resource_location: Optional[str] = None,
        multiline: Optional[bool] = None,
        provide: Optional[JsonDict] = None,
    ) -> AstRoot:
        ...

    @overload
    def parse(
        self,
        source: Union[TextFileBase[Any], str],
        *,
        type: Type[AstNodeType],
        filename: Optional[str] = None,
        resource_location: Optional[str] = None,
        multiline: Optional[bool] = None,
    ) -> AstNodeType:
        ...

    @overload
    def parse(
        self,
        source: Union[TextFileBase[Any], str],
        *,
        using: str,
        filename: Optional[str] = None,
        resource_location: Optional[str] = None,
        multiline: Optional[bool] = None,
        provide: Optional[JsonDict] = None,
    ) -> Any:
        ...

    def parse(
        self,
        source: Union[TextFileBase[Any], str],
        *,
        type: Optional[Type[AstNode]] = None,
        using: Optional[str] = None,
        filename: Optional[str] = None,
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

        if isinstance(source, str):
            source = TextFile(source)

        if not filename and source.source_path:
            filename = str(source.source_path)

        # TODO: Wrap errors in a clean FormattedPipelineException

        stream = TokenStream(source.text)
        with self.prepare_token_stream(stream, multiline=multiline):
            with stream.provide(**provide or {}):
                return delegate(parser, stream)
