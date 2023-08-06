"""Plugin for setting the log level."""


__all__ = [
    "log_level",
    "LogLevelOptions",
]

import logging
from typing import Literal

from beet import Context, PluginOptions, configurable


class LogLevelOptions(PluginOptions):
    level: Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]


def beet_default(ctx: Context):
    ctx.require(log_level)


@configurable(validator=LogLevelOptions)
def log_level(ctx: Context, opts: LogLevelOptions):
    """Plugin for setting the log level."""
    logger = logging.getLogger()
    logger.setLevel(opts.level)
