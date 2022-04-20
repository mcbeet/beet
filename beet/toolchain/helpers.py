__all__ = [
    "subproject",
    "sandbox",
    "run_beet",
    "JinjaExtension",
    "SubprojectError",
]


from contextlib import ExitStack, contextmanager
from functools import wraps
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterator, Optional, Union, overload

from jinja2 import Environment
from jinja2.ext import Extension

from beet.core.utils import FileSystemPath, JsonDict, import_from_string
from beet.toolchain.pipeline import FormattedPipelineException

from .config import ProjectConfig, config_error_handler
from .context import Context, Pipeline, Plugin, PluginSpec, ProjectCache
from .project import Project, ProjectBuilder
from .template import TemplateManager
from .worker import WorkerPool


class SubprojectError(FormattedPipelineException):
    """Raised when a subproject fails to build."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
        self.format_cause = True


@overload
def subproject(config: Union[ProjectConfig, JsonDict, FileSystemPath]) -> Plugin:
    ...


@overload
def subproject(config: Optional[str] = None, *, package: str) -> Plugin:
    ...


def subproject(
    config: Optional[Union[ProjectConfig, JsonDict, FileSystemPath]] = None,
    *,
    package: Optional[str] = None,
) -> Plugin:
    """Return a plugin that runs a subproject."""

    @wraps(subproject)
    def plugin(ctx: Context):
        project = Project(
            resolved_cache=ctx.cache,
            resolved_worker_pool=WorkerPool(resolved_handle=ctx.worker),
        )

        if isinstance(config, ProjectConfig):
            project.resolved_config = config
        elif isinstance(config, dict):
            with config_error_handler("<subproject>"):
                project.resolved_config = ProjectConfig(**config).resolve(ctx.directory)
        else:
            if package:
                whitelist = ctx.inject(Pipeline).whitelist

                try:
                    imported_package = import_from_string(package, whitelist=whitelist)
                except Exception as exc:
                    msg = (
                        f'Couldn\'t import package "{package}" for building subproject.'
                    )
                    raise SubprojectError(msg) from exc

                if filename := getattr(imported_package, "__file__", None):
                    path = Path(filename).parent
                else:
                    msg = f'Missing "__file__" attribute on package "{package}" for building subproject.'
                    raise SubprojectError(msg)

                if config:
                    path /= config

            elif config:
                path = Path(config)

            else:
                raise SubprojectError("No config provided for building subproject.")

            if path.is_dir():
                project.config_directory = path
            else:
                project.config_path = path

        ctx.require(ProjectBuilder(project))

    return plugin


def sandbox(*specs: PluginSpec) -> Plugin:
    """Return a plugin that runs the specified plugins in an isolated pipeline."""

    def plugin(ctx: Context):
        child_ctx = Context(
            project_id=ctx.project_id,
            project_name=ctx.project_name,
            project_description=ctx.project_description,
            project_author=ctx.project_author,
            project_version=ctx.project_version,
            directory=ctx.directory,
            output_directory=None,
            meta={},
            cache=ctx.cache,
            worker=ctx.worker,
            template=TemplateManager(
                templates=list(ctx.template.directories),
                cache_dir=ctx.cache["template"].directory,
            ),
        )

        with child_ctx.activate() as pipeline:
            pipeline.run(specs)

        ctx.assets.merge(child_ctx.assets)
        ctx.data.merge(child_ctx.data)

    return plugin


@contextmanager
def run_beet(
    config: Optional[Union[ProjectConfig, JsonDict, FileSystemPath]] = None,
    directory: Optional[FileSystemPath] = None,
    cache: Union[bool, ProjectCache] = False,
) -> Iterator[Context]:
    """Run the entire toolchain programmatically."""
    if not directory:
        directory = Path.cwd()

    with ExitStack() as stack:
        project = Project()

        if isinstance(cache, ProjectCache):
            project.resolved_cache = cache
        elif not cache:
            project.resolved_cache = ProjectCache(
                stack.enter_context(TemporaryDirectory()), Path(directory) / "generated"
            )

        if isinstance(config, ProjectConfig):
            project.resolved_config = config
        elif isinstance(config, dict):
            with config_error_handler("<project>"):
                project.resolved_config = ProjectConfig(**config).resolve(directory)
        elif config:
            project.config_path = config
        else:
            project.config_directory = directory

        yield ProjectBuilder(project).build()


class JinjaExtension(Extension):
    """Base extension that provides a reference to the beet context."""

    environment: Environment

    @property
    def ctx(self) -> Context:
        return getattr(self.environment, "_beet_template_manager").ctx
