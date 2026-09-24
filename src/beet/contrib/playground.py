"""Plugin for running the playground."""

__all__ = [
    "PlaygroundOptions",
    "PlaygroundArgs",
    "PlaygroundState",
    "Playground",
    "bootstrap",
    "playground_worker",
]


from dataclasses import dataclass
import logging
from pathlib import Path
import re
import subprocess
from textwrap import dedent
from threading import Event, Thread
from typing import Self, TextIO


from beet import (
    Context,
    PluginOptions,
    configurable,
    Connection,
    DataPack,
    PackOverwrite,
    Cache,
    CachePin,
    MultiCache,
)
from beet.contrib.autosave import Autosave
from beet.contrib.vanilla import Vanilla
from beet.core.utils import remove_path


logger = logging.getLogger("play")


STDOUT_REGEX = re.compile(r"\[(.+?)\] \[.+?/(DEBUG|INFO|WARN|ERROR|FATAL)\]: (.+)")


class PlaygroundOptions(PluginOptions):
    port: int | None = None
    server_properties: str = r"""
        white-list=false
        level-type=minecraft:flat
        generator-settings={"biome":"minecraft:the_void","layers":[{"block":"minecraft:air","height":1}],"features":true}
        difficulty=normal
        gamemode=creative
        motd=§cbeet §a{{ project_name }}§r\n{{ project_directory | replace("\\", "\\\\") }}
    """


@dataclass
class PlaygroundArgs:
    java: Path
    server_jar: Path
    server_properties: str
    universe: Path
    port: int | None


class PlaygroundState:
    cache: Cache

    dirty = CachePin[list[str]]("dirty", default_factory=list)

    def __init__(self, arg: Context | MultiCache[Cache] | Cache):
        if isinstance(arg, Context):
            arg = arg.cache
        if isinstance(arg, MultiCache):
            arg = arg["playground"]
        self.cache = arg

    def clean(self):
        remove_path(*[self.cache.directory / path for path in self.dirty])
        self.dirty.clear()

    def mark_dirty(self, path: Path):
        self.dirty.append("/".join(path.relative_to(self.cache.directory).parts))


@configurable("playground", validator=PlaygroundOptions)
def bootstrap(ctx: Context, opts: PlaygroundOptions):
    port = opts.port
    server_properties = dedent(ctx.template.render_string(opts.server_properties))

    state = ctx.inject(PlaygroundState)
    state.clean()

    vanilla = ctx.inject(Vanilla).shared

    with ctx.worker(playground_worker) as channel:
        channel.recv().start(
            PlaygroundArgs(
                java=vanilla.java,
                server_jar=vanilla.server_jar.path,
                server_properties=server_properties,
                universe=state.cache.directory,
                port=port,
            )
        )

    autosave = ctx.inject(Autosave)
    autosave.add_output("beet.contrib.playground")
    autosave.add_output(reload)


def beet_default(ctx: Context):
    state = ctx.inject(PlaygroundState)

    with ctx.worker(playground_worker) as channel:
        if path := channel.recv().link(ctx.data):
            state.mark_dirty(path)


def reload(ctx: Context):
    with ctx.worker(playground_worker) as channel:
        channel.recv().reload()


def playground_worker(connection: Connection[None, Playground]):
    with Playground() as playground:
        for client in connection:
            client.send(playground)
            client.close()


class Playground:
    proc: subprocess.Popen[str] | None
    args: PlaygroundArgs | None
    threads: list[Thread]
    done: Event

    def __init__(self):
        self.proc = None
        self.args = None
        self.threads = []
        self.done = Event()
        logger.addFilter(self._log_filter)

    def start(self, args: PlaygroundArgs):
        if self.args == args:
            return

        self.stop()

        args.server_jar.with_name("eula.txt").write_text("eula=true\n")
        args.server_jar.with_name("server.properties").write_text(
            args.server_properties,
            encoding="utf-8",
        )

        cmd = [args.java, "-jar", args.server_jar, "--nogui"]
        cmd += ["--universe", args.universe]
        if args.port is not None:
            cmd += ["--port", str(args.port)]

        self.proc = subprocess.Popen(
            cmd,
            cwd=args.server_jar.parent,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )

        self.args = args

        self.threads = [
            Thread(target=self._log_stdout, args=(self.proc.stdout,)),
        ]

        for thread in self.threads:
            thread.start()

    def link(self, data: DataPack) -> Path | None:
        if self.args:
            try:
                return data.save(self.args.universe / "world" / "datapacks")
            except PackOverwrite:
                pass

    def reload(self):
        if self.proc and self.done.is_set():
            assert self.proc.stdin
            self.proc.stdin.write("reload\n")
            self.proc.stdin.flush()

    def stop(self):
        self.done.clear()

        if self.proc:
            assert self.proc.stdin
            self.proc.stdin.write("stop\n")
            self.proc.stdin.flush()
            self.proc.wait()
            self.proc = None

        for thread in self.threads:
            thread.join()

        self.threads = []

    def _log_stdout(self, stdout: TextIO):
        previous_level = ""

        for line in stdout:
            fmt = "%(message)s"

            if m := STDOUT_REGEX.match(line):
                args = {"time": m[1], "level": m[2], "message": m[3]}
                extra = {}
            else:
                args = {"level": previous_level, "message": line}
                extra = {"continue": True}

            if args["level"] == "DEBUG":
                logger.debug(fmt, args, extra=extra)
            elif args["level"] == "INFO":
                logger.info(fmt, args, extra=extra)
            elif args["level"] == "WARN":
                logger.warning(fmt, args, extra=extra)
            elif args["level"] in ["ERROR", "FATAL"]:
                logger.error(fmt, args, extra=extra)

            previous_level = args["level"]

    def _log_filter(self, record: logging.LogRecord):
        if getattr(record, "continue", False):
            return True

        if not self.done.is_set() and record.getMessage().startswith("Done ("):
            self.done.set()

        return True

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_):
        self.stop()
