"""Plugin for reporting the result of the build as json."""


__all__ = [
    "JsonReporter",
    "stdout",
    "resource_pack_listing",
    "resource_pack_zip",
    "data_pack_listing",
    "data_pack_zip",
    "create_pack_listing",
    "create_pack_zip",
]


import base64
import io
import zipfile
from contextlib import contextmanager, redirect_stdout
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any, Iterator, List, Optional, Union

from beet import (
    BeetException,
    BinaryFileBase,
    Context,
    DataPack,
    ListOption,
    PluginOptions,
    PluginSpec,
    ResourcePack,
    TextFileBase,
    WrappedException,
)
from beet.core.utils import JsonDict, format_exc, get_import_string


class JsonReporterOptions(PluginOptions):
    enabled: bool = False
    binary_files: bool = False
    exception_filter: Optional[ListOption[str]] = None
    handlers: List[str] = [
        "beet.contrib.json_reporter.stdout",
        "beet.contrib.json_log",
        "beet.contrib.json_reporter.resource_pack_listing",
        "beet.contrib.json_reporter.resource_pack_zip",
        "beet.contrib.json_reporter.data_pack_listing",
        "beet.contrib.json_reporter.data_pack_zip",
    ]


def beet_default(ctx: Context):
    with ctx.inject(JsonReporter).activate() as json_reporter:
        if json_reporter.opts.enabled:
            ctx.require("beet.contrib.json_log.activate_json_log")
        yield


@dataclass
class JsonReporter:
    """Service for reporting the result of the build as json."""

    ctx: Context
    handlers: List[PluginSpec] = field(default_factory=list)
    stdout: io.StringIO = field(default_factory=io.StringIO)
    data: JsonDict = field(default_factory=lambda: {"status": "unknown"})

    def __post_init__(self):
        self.add_handler(*self.opts.handlers)

    @cached_property
    def opts(self) -> JsonReporterOptions:
        return self.ctx.validate("json_reporter", JsonReporterOptions)

    def add_handler(self, *specs: PluginSpec):
        self.handlers.extend(specs)

    @contextmanager
    def activate(self) -> Iterator["JsonReporter"]:
        if not self.opts.enabled:
            yield self
            return

        message = None
        exception = None

        try:
            with redirect_stdout(self.stdout):
                yield self
        except WrappedException as exc:
            message = str(exc)
            if not exc.hide_wrapped_exception:
                exception = exc.__cause__
        except BeetException as exc:
            message = str(exc)
        except Exception as exc:
            message = "An unhandled exception occurred. This could be a bug."
            exception = exc

        if message is None:
            self.data["status"] = "success"
        else:
            self.data["status"] = "error"
            error = self.data.setdefault("error", {})

            error["message"] = message

            exc_fullname = get_import_string(type(exception))

            if exception is None:
                traceback = None
            elif self.opts.exception_filter is None:
                traceback = format_exc(exception)
            elif any(f in exc_fullname for f in self.opts.exception_filter.entries()):
                traceback = f"{type(exception).__name__}: {exception}\n"
            else:
                traceback = f'{type(exception).__name__}: Disable the "exception_filter" option to see the full traceback.\n'

            error["exception"] = traceback

        self.ctx.require(*self.handlers)


def stdout(ctx: Context):
    json_reporter = ctx.inject(JsonReporter)
    json_reporter.data["stdout"] = json_reporter.stdout.getvalue()


def resource_pack_listing(ctx: Context):
    json_reporter = ctx.inject(JsonReporter)
    json_reporter.data.setdefault("resource_pack", {}).update(
        create_pack_listing(ctx.assets, json_reporter.opts.binary_files)
    )


def resource_pack_zip(ctx: Context):
    json_reporter = ctx.inject(JsonReporter)
    json_reporter.data.setdefault("resource_pack", {}).update(
        create_pack_zip(ctx.assets)
    )


def data_pack_listing(ctx: Context):
    json_reporter = ctx.inject(JsonReporter)
    json_reporter.data.setdefault("data_pack", {}).update(
        create_pack_listing(ctx.data, json_reporter.opts.binary_files)
    )


def data_pack_zip(ctx: Context):
    json_reporter = ctx.inject(JsonReporter)
    json_reporter.data.setdefault("data_pack", {}).update(create_pack_zip(ctx.data))


def create_pack_listing(
    pack: Union[ResourcePack, DataPack],
    binary_files: bool = False,
) -> JsonDict:
    listing: JsonDict = {
        "name": pack.name,
        "description": pack.description,
        "pack_format": pack.pack_format,
        "empty": not pack,
    }

    listing["text_files"] = {
        k: v.text for k, v in pack.list_files(extend=TextFileBase[Any])
    }

    if binary_files:
        listing["binary_files"] = {
            k: base64.b64encode(v.blob).decode()
            for k, v in pack.list_files(extend=BinaryFileBase[Any])
        }

    return listing


def create_pack_zip(pack: Union[ResourcePack, DataPack]) -> JsonDict:
    fileobj = io.BytesIO()
    with zipfile.ZipFile(fileobj, mode="w") as output:
        pack.dump(output)
    return {"zip": base64.b64encode(fileobj.getvalue()).decode()}
