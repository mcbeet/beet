__all__ = [
    "Mecha",
]


from contextlib import contextmanager
from dataclasses import InitVar, dataclass, replace
from typing import Any, Iterator, List, Optional, Union

from beet import Context, Function, TextFileBase
from beet.core.utils import extra_field
from tokenstream import TokenStream

from .ast import AstCommand, AstRoot
from .parse import delegate, get_default_parsers
from .spec import CommandSpec


@dataclass
class Mecha:
    """Class exposing the command api."""

    ctx: InitVar[Optional[Context]] = None

    spec: CommandSpec = extra_field(
        default_factory=lambda: CommandSpec(parsers=get_default_parsers())
    )

    @contextmanager
    def prepare_token_stream(self, stream: TokenStream) -> Iterator[TokenStream]:
        """Prepare the token stream for parsing."""
        with stream.provide(spec=self.spec), stream.syntax(literal=r"\S+"):
            yield stream

    def parse_function(
        self,
        function: Union[TextFileBase[Any], str, List[str]],
        filename: Optional[str] = None,
    ) -> AstRoot:
        """Parse a function and return the ast."""
        if isinstance(function, (str, list)):
            function = Function(function)

        if not filename and function.source_path:
            filename = str(function.source_path)

        with self.prepare_token_stream(TokenStream(function.text)) as stream:
            return replace(delegate("root", stream), filename=filename)

    def parse_command(self, text: str) -> AstCommand:
        """Parse a single command from a string and return the ast."""
        with self.prepare_token_stream(TokenStream(text)) as stream:
            return delegate("command", stream)
