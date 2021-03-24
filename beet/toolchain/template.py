__all__ = [
    "TemplateError",
    "TemplateManager",
]


from contextlib import contextmanager
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
from jinja2.ext import ExprStmtExtension, LoopControlExtension, WithExtension
from jinja2.loaders import BaseLoader

from beet.core.file import TextFileBase
from beet.core.utils import FileSystemPath

from .pipeline import FormattedPipelineException, PipelineFallthroughException

TextFileType = TypeVar("TextFileType", bound=TextFileBase[Any])


class TemplateError(FormattedPipelineException):
    """Raised when an error occurs during template rendering."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
        self.format_cause = True


class TemplateManager:
    """Class responsible for managing the Jinja environment."""

    env: Environment
    loaders: List[BaseLoader]
    prefix_map: Dict[str, BaseLoader]
    directories: List[FileSystemPath]

    def __init__(self, templates: List[FileSystemPath], cache_dir: FileSystemPath):
        self.prefix_map = {}
        self.directories = templates

        self.loaders = [
            FileSystemLoader(self.directories),
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
        except PipelineFallthroughException:
            raise
        except Exception as exc:
            tb = exc.__traceback__
            while tb:
                if "__jinja_exception__" in tb.tb_frame.f_globals:
                    exc = exc.with_traceback(tb)
                tb = tb.tb_next
            raise TemplateError(message) from exc
