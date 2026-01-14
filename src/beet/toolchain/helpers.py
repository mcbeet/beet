__all__ = [
    "subproject",
    "sandbox",
    "run_beet",
    "JinjaExtension",
]


from contextlib import contextmanager
from functools import wraps
from pathlib import Path
from typing import Iterator, Optional, Union

from jinja2 import Environment
from jinja2.ext import Extension

from beet.core.utils import FileSystemPath, JsonDict

from .config import ProjectConfig, config_error_handler
from .context import Context, Plugin, PluginSpec, ProjectCache
from .project import Project, ProjectBuilder
from .template import TemplateManager
from .worker import WorkerPool


def subproject(config: Union[ProjectConfig, JsonDict, FileSystemPath]) -> Plugin:
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
            with config_error_handler("(subproject)"):
                project.resolved_config = ProjectConfig(**config).resolve(ctx.directory)
        else:
            project.config_path = config

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
            project_root=False,
            minecraft_version=ctx.minecraft_version,
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

    tmpdir = False
    project = Project()

    if isinstance(cache, ProjectCache):
        project.resolved_cache = cache
    elif not cache:
        tmpdir = True

    if isinstance(config, ProjectConfig):
        project.resolved_config = config
    elif isinstance(config, dict):
        with config_error_handler("(project)"):
            project.resolved_config = ProjectConfig(**config).resolve(directory)
    else:
        project.config_path = config or directory

    with ProjectBuilder(project, root=True, tmpdir=tmpdir).build() as ctx:
        yield ctx


class JinjaExtension(Extension):
    """Base extension that provides a reference to the beet context."""

    environment: Environment

    @property
    def ctx(self) -> Context:
        return getattr(self.environment, "_beet_template_manager").ctx
