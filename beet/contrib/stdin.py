"""Plugin that builds a project from standard input."""


import json
import sys

from beet import (
    Context,
    ErrorMessage,
    Project,
    ProjectBuilder,
    ProjectConfig,
    WorkerPool,
    config_error_handler,
)


def beet_default(ctx: Context):
    if ctx.worker.long_lived:
        raise ErrorMessage(
            f'The "{__name__}" plugin should only be used for one-shot builds.'
        )

    with config_error_handler("(stdin)"):
        data = json.load(sys.stdin)
        config = ProjectConfig.parse_obj(data).resolve(ctx.directory)

    ctx.require(
        ProjectBuilder(
            Project(
                resolved_config=config,
                resolved_cache=ctx.cache,
                resolved_worker_pool=WorkerPool(resolved_handle=ctx.worker),
            )
        )
    )
