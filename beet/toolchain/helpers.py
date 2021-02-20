__all__ = [
    "subproject",
    "sandbox",
]


from pathlib import Path
from typing import Union

from beet.core.utils import FileSystemPath, JsonDict

from .config import ProjectConfig, config_error_handler
from .context import Context, Plugin, PluginSpec
from .project import Project, ProjectBuilder
from .template import TemplateManager


def subproject(config: Union[ProjectConfig, JsonDict, FileSystemPath]) -> Plugin:
    """Return a plugin that runs a subproject."""

    def plugin(ctx: Context):
        project = Project(resolved_cache=ctx.cache)

        if isinstance(config, ProjectConfig):
            project.resolved_config = config
        elif isinstance(config, dict):
            with config_error_handler("<subproject>"):
                project.resolved_config = ProjectConfig(**config).resolve(ctx.directory)
        else:
            path = Path(config)

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
            project_name=ctx.project_name,
            project_description=ctx.project_description,
            project_author=ctx.project_author,
            project_version=ctx.project_version,
            directory=ctx.directory,
            output_directory=None,
            meta={},
            cache=ctx.cache,
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
