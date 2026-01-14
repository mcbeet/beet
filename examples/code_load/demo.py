from beet import Context, Project, ProjectBuilder, ProjectConfig, WorkerPool


def beet_default(ctx: Context):
    config = ProjectConfig(data_pack={"load": ["src"]}).resolve(ctx.directory)  # pyright: ignore[reportArgumentType]
    ctx.require(
        ProjectBuilder(
            Project(
                config,
                resolved_cache=ctx.cache,
                resolved_worker_pool=WorkerPool(resolved_handle=ctx.worker),
            )
        )
    )
