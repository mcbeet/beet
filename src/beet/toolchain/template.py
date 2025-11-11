__all__ = [
    "TemplateError",
    "TemplateManager",
    "FallbackContext",
]


from contextlib import contextmanager
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

from jinja2 import (
    BaseLoader,
    ChoiceLoader,
    Environment,
    FileSystemBytecodeCache,
    FileSystemLoader,
    PackageLoader,
    PrefixLoader,
    Template,
)
from jinja2.ext import DebugExtension, ExprStmtExtension, LoopControlExtension
from jinja2.runtime import Context as JinjaContext
from jinja2.utils import missing as jinja_missing

from beet.core.error import BubbleException, WrappedException
from beet.core.file import TextFileBase
from beet.core.utils import FileSystemPath, JsonDict

from .utils import ensure_builtins

T = TypeVar("T")
TextFileType = TypeVar("TextFileType", bound=TextFileBase[Any])


class TemplateError(WrappedException):
    """Raised when an error occurs during template rendering."""

    message: str

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return self.message


class FallbackContext(JinjaContext):
    """Template context that falls back to globals and meta entries."""

    def resolve_or_missing(self, key: str) -> Any:
        value: Any = super().resolve_or_missing(key)

        if value is jinja_missing:
            manager: TemplateManager = getattr(
                self.environment, "_beet_template_manager"
            )

            if key in manager.globals:
                return manager.globals[key]

            if key == "project_directory":
                return manager.ctx.project_directory

            if key in [
                "project_id",
                "project_name",
                "project_description",
                "project_author",
                "project_version",
            ]:
                return getattr(manager.ctx, key)

            try:
                return ensure_builtins(manager.ctx.meta[key])
            except (KeyError, TypeError):
                pass

        return value


class TemplateManager:
    """Class responsible for managing the Jinja environment."""

    env: Environment
    loaders: List[BaseLoader]
    prefix_map: Dict[str, BaseLoader]
    directories: List[FileSystemPath]
    cache_dir: FileSystemPath
    ctx: Any
    globals: JsonDict

    def __init__(self, templates: List[FileSystemPath], cache_dir: FileSystemPath):
        self.prefix_map = {}
        self.directories = templates
        self.cache_dir = cache_dir
        self.ctx = None
        self.globals = {}

        self.loaders = [
            FileSystemLoader(self.directories),
            PrefixLoader(self.prefix_map),
        ]

        self.reset_environment()

    def reset_environment(self, cls: Type[Environment] = Environment):
        """Reset the Jinja environment."""
        self.env = cls(
            autoescape=False,
            line_statement_prefix="#!",
            keep_trailing_newline=True,
            loader=ChoiceLoader(self.loaders),
            bytecode_cache=FileSystemBytecodeCache(str(self.cache_dir)),
            extensions=[
                DebugExtension,
                ExprStmtExtension,
                LoopControlExtension,
            ],
        )

        setattr(self.env, "_beet_template_manager", self)
        self.env.context_class = FallbackContext

    def bind(self, ctx: Any):
        """Bind the template maneger instance to the beet context."""
        self.ctx = ctx

    def expose(self, name: str, function: Callable[..., Any]):
        """Expose a utility function to the template context."""
        self.globals[name] = lambda *args, **kwargs: function(*args, **kwargs)  # type: ignore

    def add_package(self, dotted_path: str, prefix: Optional[str] = None):
        """Make the templates included in the specified package available."""
        if not prefix:
            prefix = dotted_path.replace(".", "/")
        self.prefix_map[prefix] = PackageLoader(dotted_path)

    def compile(
        self,
        source: str,
        filename: Optional[FileSystemPath] = None,
    ) -> Template:
        """Compile a template from a string."""
        return Template.from_code(
            self.env,
            self.env.compile(source, filename=str(filename) if filename else None),
            self.env.make_globals(None),
        )

    def render(self, filename: str, /, **kwargs: Any) -> str:
        """Render the specified template."""
        with self.error_handler(f"Couldn't render template {filename!r}."):
            return self.env.get_template(filename).render(kwargs)

    def render_string(self, template: str, /, **kwargs: Any) -> str:
        """Render a string template."""
        with self.error_handler("Couldn't render template."):
            return self.compile(template).render(kwargs)

    def render_file(self, file: TextFileType, /, **kwargs: Any) -> TextFileType:
        """Render a given file in-place."""
        original_path = file.source_path
        try:
            source = file.text
            with self.error_handler("Couldn't render file."):
                template = self.compile(source, filename=original_path)
                file.text = template.render(kwargs)
            return file
        except OSError:
            if not original_path:
                raise
        file.text = self.render(str(original_path), **kwargs)
        return file

    def render_json(self, data: T, /, **kwargs: Any) -> T:
        """Render all strings in a json value."""
        if isinstance(data, str):
            return self.render_string(data, **kwargs)  # type: ignore
        elif isinstance(data, list):
            return [self.render_json(element, **kwargs) for element in data]  # type: ignore
        elif isinstance(data, dict):
            return {key: self.render_json(value, **kwargs) for key, value in data.items()}  # type: ignore
        else:
            return data

    @contextmanager
    def error_handler(self, message: str):
        """Handle template errors."""
        try:
            yield
        except BubbleException:
            raise
        except Exception as exc:
            tb = exc.__traceback__
            while tb:
                if "__jinja_exception__" in tb.tb_frame.f_globals:
                    exc = exc.with_traceback(tb)
                tb = tb.tb_next
            raise TemplateError(message) from exc
