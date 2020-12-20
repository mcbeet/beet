__all__ = [
    "TemplateError",
    "TemplateManager",
    "DedentExtension",
]


from contextlib import contextmanager
from textwrap import dedent
from typing import Any, Dict, List, Optional, TypeVar

from jinja2 import (
    BaseLoader,
    ChoiceLoader,
    Environment,
    FileSystemBytecodeCache,
    FileSystemLoader,
    PackageLoader,
    PrefixLoader,
)
from jinja2.ext import DebugExtension  # type: ignore
from jinja2.ext import ExprStmtExtension, Extension, LoopControlExtension, WithExtension
from jinja2.lexer import Token
from jinja2.loaders import BaseLoader

from beet.core.file import TextFileBase
from beet.core.utils import FileSystemPath

TextFileType = TypeVar("TextFileType", bound=TextFileBase[Any])


class TemplateError(Exception):
    """Raised when an error occurs during template rendering."""


class TemplateManager:
    """Class responsible for managing the Jinja environment."""

    env: Environment
    loaders: List[BaseLoader]
    prefix_map: Dict[str, BaseLoader]

    def __init__(self, templates: List[FileSystemPath], cache_dir: FileSystemPath):
        self.prefix_map = {}

        self.loaders = [
            FileSystemLoader(templates),
            PrefixLoader(self.prefix_map),
        ]

        self.env = Environment(
            autoescape=False,
            line_statement_prefix="#!",
            keep_trailing_newline=True,
            loader=ChoiceLoader(self.loaders),
            bytecode_cache=FileSystemBytecodeCache(cache_dir),
            extensions=[
                DebugExtension,
                ExprStmtExtension,
                LoopControlExtension,
                WithExtension,
                DedentExtension,
            ],
        )

    def add_package(self, dotted_path: str, prefix: Optional[str] = None):
        """Make the templates included in the specified package available."""
        if not prefix:
            prefix = dotted_path.replace(".", "/")
        self.prefix_map[prefix] = PackageLoader(dotted_path)

    def render(self, filename: str, **kwargs: Any) -> str:
        """Render the specified template."""
        with self.error_handler(f"Couldn't render template {filename!r}."):
            return self.env.get_template(filename).render(kwargs)  # type: ignore

    def render_string(self, template: str, **kwargs: Any) -> str:
        """Render a string template."""
        with self.error_handler("Couldn't render template."):
            return self.env.from_string(template).render(kwargs)  # type: ignore

    def render_file(self, file: TextFileType, **kwargs: Any) -> TextFileType:
        """Render a given file in-place."""
        file.text = self.render_string(file.text, **kwargs)
        return file

    @contextmanager
    def error_handler(self, message: str):
        """Handle template errors."""
        try:
            yield
        except TemplateError:
            raise
        except Exception as exc:
            tb = exc.__traceback__
            while tb:
                if "__jinja_exception__" in tb.tb_frame.f_globals:
                    exc = exc.with_traceback(tb)
                tb = tb.tb_next
            raise TemplateError(message) from exc


class DedentExtension(Extension):
    """Extension that removes indention from templates."""

    def filter_stream(self, stream: Any):
        lineno = 0
        for token in stream:
            if token.type == "data":
                prefix, newline, value = token.value.partition("\n")
                if token.lineno > lineno:
                    prefix = dedent(prefix)
                token = Token(token.lineno, "data", prefix + newline + dedent(value))
            yield token
            lineno = token.lineno
