__all__ = [
    "Pipeline",
    "Plugin",
    "PluginSpec",
    "PluginWithOptions",
    "ConfigurablePlugin",
    "ServiceFactory",
    "Validator",
    "ProjectCache",
    "Context",
    "ContextContainer",
    "ErrorMessage",
    "InvalidOptions",
    "configurable",
]


import json
import sys
from contextlib import contextmanager
from dataclasses import InitVar, dataclass, field
from functools import partial, wraps
from pathlib import Path
from typing import (
    Any,
    Callable,
    List,
    Optional,
    Protocol,
    Set,
    Tuple,
    Type,
    TypeVar,
    overload,
)

from pydantic import ValidationError

from beet.core.cache import Cache, MultiCache
from beet.core.container import Container
from beet.core.utils import (
    FileSystemPath,
    JsonDict,
    TextComponent,
    extra_field,
    import_from_string,
)
from beet.library.data_pack import DataPack
from beet.library.resource_pack import ResourcePack

from .generator import Generator
from .pipeline import (
    FormattedPipelineException,
    GenericPipeline,
    GenericPlugin,
    GenericPluginSpec,
    PipelineFallthroughException,
)
from .template import TemplateManager
from .tree import generate_tree
from .utils import format_validation_error
from .worker import WorkerPoolHandle

T = TypeVar("T")
OptionsType = TypeVar("OptionsType", contravariant=True)

Plugin = GenericPlugin["Context"]
PluginSpec = GenericPluginSpec["Context"]
ServiceFactory = Callable[["Context"], T]
Validator = Callable[..., T]


class ErrorMessage(FormattedPipelineException):
    """Exception used to display nice error messages when something goes wrong."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class InvalidOptions(FormattedPipelineException):
    """Raised when a validation error occurs."""

    key: str
    explanation: Optional[str]

    def __init__(self, key: str, explanation: Optional[str] = None):
        super().__init__(key, explanation)
        self.key = key
        self.explanation = explanation
        self.message = f"Invalid options {key!r}."
        self.format_cause = True

        if explanation:
            self.message += f"\n\n{explanation}"


@dataclass
class Pipeline(GenericPipeline["Context"]):
    ctx: "Context"


class PluginWithOptions(Protocol[OptionsType]):
    def __call__(self, ctx: "Context", opts: OptionsType, /) -> Any:
        ...


class ConfigurablePlugin(Protocol):
    @overload
    def __call__(self, ctx: "Context", /) -> Any:
        ...

    @overload
    def __call__(self, **kwds: Any) -> "ConfigurablePlugin":
        ...


class ContextContainer(Container[Callable[["Context"], Any], Any]):
    """Dict-like container that instantiates and holds objects injected into the context."""

    def __init__(self, ctx: "Context"):
        super().__init__()
        self.ctx = ctx

    def missing(self, key: Callable[["Context"], Any]) -> Any:
        return key(self.ctx)


class ProjectCache(MultiCache[Cache]):
    """The project cache.

    The `generated` attribute is a MultiCache instance that's
    meant to be tracked by version control, unlike the main project
    cache that usually lives in the ignored `.beet_cache` directory.
    """

    generated: MultiCache[Cache]

    def __init__(
        self,
        directory: FileSystemPath,
        generated_directory: FileSystemPath,
        default_cache: str = "default",
        gitignore: bool = True,
        cache_type: Type[Cache] = Cache,
    ):
        super().__init__(directory, default_cache, gitignore, cache_type=Cache)
        self.generated = MultiCache(
            generated_directory,
            default_cache,
            gitignore=False,
            cache_type=cache_type,
        )

    def flush(self):
        super().flush()
        self.generated.flush()


@dataclass
class Context:
    """The build context."""

    project_id: str
    project_name: str
    project_description: TextComponent
    project_author: str
    project_version: str

    directory: Path
    output_directory: Optional[Path]
    meta: JsonDict
    cache: ProjectCache
    worker: WorkerPoolHandle
    template: TemplateManager
    generate: Generator = field(init=False)

    assets: ResourcePack = field(default_factory=ResourcePack)
    data: DataPack = field(default_factory=DataPack)

    whitelist: InitVar[Optional[List[str]]] = None

    _container: ContextContainer = extra_field(init=False)
    _path_entry: str = extra_field(init=False)

    def __post_init__(self, whitelist: Optional[List[str]]):
        self._container = ContextContainer(self)
        self._path_entry = str(self.directory.resolve())

        self.generate = self.inject(Generator)
        self.generate.assets = self.assets
        self.generate.data = self.data

        self.inject(Pipeline).whitelist = whitelist
        self.template.bind(self)

        self.template.expose("generate_path", self.generate.path)
        self.template.expose("generate_id", self.generate.id)
        self.template.expose("generate_hash", self.generate.hash)
        self.template.expose("generate_objective", self.generate.objective)
        self.template.expose(
            "generate_tree",
            lambda *args, **kwargs: generate_tree(
                kwargs.pop("root") if "root" in kwargs else self.meta["render_path"],
                *args,
                name=(
                    kwargs.pop("name")
                    if "name" in kwargs
                    else self.generate["tree"][self.meta["render_path"]].format(
                        "tree_{incr}"
                    )
                ),
                **kwargs,
            ),
        )

        self.template.expose("parse_json", lambda string: json.loads(string))

    @overload
    def inject(self, cls: ServiceFactory[T]) -> T:
        ...

    @overload
    def inject(self, cls: str) -> Any:
        ...

    def inject(self, cls: Any) -> Any:
        """Retrieve the instance provided by the specified service factory."""
        if not callable(cls):
            cls = import_from_string(cls, whitelist=self.inject(Pipeline).whitelist)
        return self._container[cls]

    @contextmanager
    def activate(self):
        """Push the context directory to sys.path and handle cleanup to allow module reloading."""
        already_loaded = set(sys.modules)

        not_in_path = self._path_entry not in sys.path
        if not_in_path:
            sys.path.append(self._path_entry)

        try:
            with self.cache:
                yield self.inject(Pipeline)
        finally:
            if not_in_path:
                sys.path.remove(self._path_entry)

            imported_modules = [
                name
                for name, module in sys.modules.items()
                if name not in already_loaded
                and (filename := getattr(module, "__file__", None))
                and "site-packages" not in filename
                and filename.startswith(self._path_entry)
            ]

            for name in imported_modules:
                del sys.modules[name]

    @contextmanager
    def override(self, **meta: Any):
        """Temporarily update the context meta."""
        to_restore: JsonDict = {}
        to_remove: Set[str] = set()

        for key, value in meta.items():
            if key in self.meta:
                to_restore[key] = self.meta[key]
            else:
                to_remove.add(key)
            self.meta[key] = value

        try:
            yield self
        finally:
            for key in to_remove:
                del self.meta[key]
            self.meta.update(to_restore)

    def validate(
        self,
        key: str,
        validator: Validator[T],
        options: Optional[JsonDict] = None,
    ) -> T:
        """Validate options."""
        if options is None:
            options = self.meta.get(key)
        try:
            return validator(**(options or {}))
        except ValidationError as exc:
            explanation = format_validation_error(key, exc)
            raise InvalidOptions(key, explanation) from None
        except PipelineFallthroughException:
            raise
        except Exception as exc:
            raise InvalidOptions(key) from exc

    @property
    def packs(self) -> Tuple[ResourcePack, DataPack]:
        return self.assets, self.data

    def require(self, *args: PluginSpec):
        """Execute the specified plugin."""
        self.inject(Pipeline).require(*args)


@overload
def configurable(
    name: Optional[str] = None,
    /,
    *,
    validator: Validator[OptionsType],
) -> Callable[[PluginWithOptions[OptionsType]], ConfigurablePlugin]:
    ...


@overload
def configurable(
    name: Optional[str] = None,
    /,
) -> Callable[[PluginWithOptions[JsonDict]], ConfigurablePlugin]:
    ...


@overload
def configurable(plugin: PluginWithOptions[JsonDict]) -> ConfigurablePlugin:
    ...


def configurable(
    plugin: Any = None,
    *,
    name: Optional[str] = None,
    validator: Optional[Validator[Any]] = None,
) -> Any:
    """Decorator for making a plugin configurable."""
    if not callable(plugin):
        if isinstance(plugin, str):
            name = plugin
        return partial(configurable, name=name, validator=validator)

    @wraps(plugin)
    def wrapper(ctx: Optional[Context] = None, /, **kwargs: Any) -> Any:
        if ctx is None:
            return partial(wrapper, **kwargs)
        return plugin(
            ctx,
            ctx.validate(
                key=name or plugin.__name__,
                validator=validator or (lambda **kw: kw),
                options=kwargs or None,
            ),
        )

    return wrapper
