"""Plugin for collecting json logs."""

__all__ = [
    "JsonLogEntry",
    "JsonLogHandler",
    "activate_json_log",
]


import logging
from contextlib import contextmanager

from pydantic import BaseModel

from beet import Context
from beet.contrib.json_reporter import JsonReporter
from beet.toolchain.cli import LogHandler


class JsonLogEntry(BaseModel):
    level: str
    prefix: str
    message: str
    annotation: str | None
    details: list[str]


def activate_json_log(ctx: Context):
    with ctx.inject(JsonLogHandler).activate():
        yield


def beet_default(ctx: Context):
    json_reporter = ctx.inject(JsonReporter)
    json_reporter.data["log"] = [
        entry.model_dump() for entry in ctx.inject(JsonLogHandler).entries
    ]


class JsonLogHandler(LogHandler):
    """Logging handler that collects log records as json."""

    entries: list[JsonLogEntry]

    def __init__(self, ctx: Context | None = None):
        super().__init__()
        self.entries = []

    @contextmanager
    def activate(self):
        logger = logging.getLogger()
        previous_handlers = logger.handlers
        logger.handlers = [self]

        try:
            yield
        finally:
            logger.handlers = previous_handlers

    def emit(self, record: logging.LogRecord):
        level = self.abbreviations.get(record.levelname, record.levelname)
        leading_line, *lines = self.format(record).splitlines()

        self.entries.append(
            JsonLogEntry(
                level=level,
                prefix=getattr(record, "prefix", record.name),
                message=leading_line,
                annotation=getattr(record, "annotate", None),
                details=lines,
            )
        )
