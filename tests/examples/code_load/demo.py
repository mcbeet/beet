from beet import Context, Project, ProjectBuilder, ProjectConfig


def beet_default(ctx: Context):
    config = ProjectConfig(data_pack={"load": ["src"]}).resolve(ctx.directory)
    ctx.require(ProjectBuilder(Project(config, resolved_cache=ctx.cache)))
