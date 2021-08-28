__all__ = [
    "Mecha",
]


from dataclasses import InitVar, dataclass, replace
from typing import Any, List, Optional, Union

from beet import Context, Function, TextFileBase
from beet.core.utils import extra_field
from tokenstream import TokenStream

from .ast import AstCommand, AstRoot
from .parse import delegate, get_default_parsers
from .spec import CommandSpecification


@dataclass
class Mecha:
    """Class exposing the command api."""

    ctx: InitVar[Optional[Context]] = None

    spec: CommandSpecification = extra_field(
        default_factory=lambda: CommandSpecification(parsers=get_default_parsers())
    )

    def create_token_stream(self, text: str) -> TokenStream:
        """Instantiate a token stream for parsing the given input."""
        stream = TokenStream(text)
        stream.data["spec"] = self.spec
        return stream

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

        ast = delegate("root", self.create_token_stream(function.text + "\n"))
        return replace(ast, filename=filename)

    def parse_command(self, command: str) -> AstCommand:
        """Parse a single command from a string and return the ast."""
        ast = self.parse_function(command)

        if len(ast.commands) != 1:
            raise ValueError(
                "Expected a single command but more than one command were provided."
                if ast.commands
                else "Expected a single command but no command were provided.",
            )

        return ast.commands[0]
