"""Singleton for managing a background process running a minecraft server."""

__all__ = [
    "PlaygroundOptions",
    "PlaygroundArgs",
    "Playground",
    "start",
    "stop",
    "link",
    "clean",
    "reload",
    "playground_logs",
    "PlaygroundListener",
]


from collections.abc import Generator, Iterable
from contextlib import contextmanager
from dataclasses import dataclass
import logging
from pathlib import Path
from queue import Empty, Queue, ShutDown
import re
import subprocess
from textwrap import dedent
from threading import Condition, Thread
from typing import Self

from beet import Context, PluginOptions, configurable, PackOverwrite
from beet.contrib.link import LinkManager
from beet.contrib.singleton import singleton
from beet.contrib.vanilla import Vanilla
from beet.core.utils import JsonDict, remove_path


class PlaygroundOptions(PluginOptions):
    server_properties: str = r"""
        white-list=false
        pause-when-empty-seconds=86400
        level-type=minecraft:flat
        generator-settings={"biome":"minecraft:the_void","layers":[{"block":"minecraft:air","height":1}],"features":true}
        difficulty=normal
        gamemode=creative
        motd=§a{{ project_name }} §4(beet)§r\n{{ project_directory | replace("\\", "\\\\") }}
    """
    port: int | None = None


@dataclass
class PlaygroundArgs:
    java: Path
    server_jar: Path
    server_properties: str
    world: Path
    port: int | None


def beet_default(ctx: Context):
    ctx.require(start)


@configurable("playground", validator=PlaygroundOptions)
def start(ctx: Context, opts: PlaygroundOptions):
    """Plugin to start the playground."""
    link_manager = ctx.inject(LinkManager)
    vanilla = ctx.inject(Vanilla)
    cache = ctx.cache["playground"]

    args = PlaygroundArgs(
        java=vanilla.shared.java,
        server_jar=vanilla.shared.server_jar.path,
        server_properties=dedent(ctx.template.render_string(opts.server_properties)),
        world=Path(link_manager.world or cache.directory / "world").resolve(),
        port=opts.port,
    )

    playground = ctx.inject(singleton(Playground))
    playground.start(args)


def stop(ctx: Context):
    """Plugin to stop the playground."""
    playground = ctx.inject(singleton(Playground))
    playground.stop()


def link(ctx: Context):
    """Plugin to copy the data pack to the world opened in the playground."""
    cache = ctx.cache["playground"]
    dirty = cache.json.setdefault("dirty", [])

    playground = ctx.inject(singleton(Playground))
    with playground.cond:
        if playground.args:
            try:
                path = ctx.data.save(playground.args.world / "datapacks")
            except PackOverwrite:
                pass
            else:
                if cache.directory in path.parents:
                    path = "/".join(path.relative_to(cache.directory).parts)
                dirty.append(str(path))


def clean(ctx: Context):
    """Plugin to remove the data pack previously linked to the playground."""
    cache = ctx.cache["playground"]
    dirty = cache.json.setdefault("dirty", [])

    playground = ctx.inject(singleton(Playground))
    with playground.cond:
        remove_path(*[cache.directory / path for path in dirty])

    dirty.clear()


def reload(ctx: Context):
    """Plugin to make the playground reload data packs."""
    playground = ctx.inject(singleton(Playground))
    playground.run("reload")


class Playground:
    cond: Condition
    proc: subprocess.Popen[str] | None
    args: PlaygroundArgs | None
    ready: bool

    def __init__(self):
        self.cond = Condition()
        self.proc = None
        self.args = None
        self.ready = False

    def start(self, args: PlaygroundArgs):
        with self.cond:
            if self.args == args:
                return

            self.stop()

            level_name = str(args.world).replace("\\", "\\\\")

            server_properties = args.server_properties
            server_properties += f"\nlevel-name={level_name}\n"

            args.server_jar.with_name("eula.txt").write_text("eula=true\n")
            args.server_jar.with_name("server.properties").write_text(
                server_properties,
                encoding="utf-8",
            )

            cmd = [args.java, "-jar", args.server_jar, "--nogui"]
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

            Thread(target=self._daemon, args=(self.proc,), daemon=True).start()

    def stop(self):
        with self.cond:
            if self.ready:
                self.run("stop")
            elif self.proc:
                self.proc.kill()
            self.cond.wait_for(lambda: self.proc is None)

    def run(self, command: str):
        with self.cond:
            self.cond.wait_for(lambda: self.ready or self.proc is None)
            if self.proc:
                assert self.proc.stdin
                self.proc.stdin.write(command.strip() + "\n")
                self.proc.stdin.flush()

    def _daemon(self, proc: subprocess.Popen[str]):
        game = logging.getLogger("game")
        game.addFilter(_filter_game_log)

        regex = re.compile(r"\[(.+?)\] \[.+?/(DEBUG|INFO|WARN|ERROR|FATAL)\]: (.+)")
        previous_level = ""

        assert proc.stdout
        for line in proc.stdout:
            extra: JsonDict = {"raw": line}

            if m := regex.match(line):
                level = m[2]
                message = m[3]
                if message.startswith("Done ("):
                    with self.cond:
                        if not self.ready:
                            self.ready = True
                            self.cond.notify_all()
            else:
                level = previous_level
                message = line
                extra["continue"] = True

            if level == "DEBUG":
                game.debug(message, extra=extra)
            elif level == "INFO":
                game.info(message, extra=extra)
            elif level == "WARN":
                game.warning(message, extra=extra)
            elif level in ["ERROR", "FATAL"]:
                game.error(message, extra=extra)

            previous_level = level

        with self.cond:
            proc.wait()
            self.proc = None
            self.args = None
            self.ready = False
            self.cond.notify_all()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_):
        self.stop()


def _filter_game_log(record: logging.LogRecord) -> bool:
    record.msg = record.getMessage().removeprefix("[Not Secure] ")
    return True


@contextmanager
def playground_logs(timeout: float | None = None) -> Generator[Iterable[str]]:
    listener = PlaygroundListener()

    game = logging.getLogger("game")
    game.addFilter(listener)
    try:
        yield listener.collect(timeout)
    finally:
        game.removeFilter(listener)
        listener.queue.shutdown()


class PlaygroundListener:
    queue: Queue[str]

    def __init__(self):
        self.queue = Queue()

    def __call__(self, record: logging.LogRecord) -> bool:
        raw = getattr(record, "raw", None)
        if raw is not None:
            self.queue.put(raw)
        return True

    def collect(self, timeout: float | None = None) -> Iterable[str]:
        while True:
            try:
                yield self.queue.get(timeout=timeout)
            except ShutDown, Empty:
                break
