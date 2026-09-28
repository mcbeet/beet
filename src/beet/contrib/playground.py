"""Plugin for running the playground."""

__all__ = [
    "PlaygroundOptions",
    "PlaygroundArgs",
    "Playground",
    "bootstrap",
    "start",
    "stop",
    "link",
    "reload",
    "playground_worker",
    "ServerThread",
    "PlaygroundNotStarted",
]


from collections.abc import Generator, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
import logging
from pathlib import Path
from queue import Empty, Queue, ShutDown
import re
import subprocess
from textwrap import dedent
from threading import Event, Thread

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
from beet.contrib.link import LinkManager
from beet.contrib.vanilla import Vanilla
from beet.core.utils import FileSystemPath, remove_path


class PlaygroundNotStarted(Exception):
    """Raised when trying to exec a command but the playground was not started."""


class PlaygroundOptions(PluginOptions):
    port: int | None = None
    server_properties: str = r"""
        white-list=false
        pause-when-empty-seconds=86400
        level-type=minecraft:flat
        generator-settings={"biome":"minecraft:the_void","layers":[{"block":"minecraft:air","height":1}],"features":true}
        difficulty=normal
        gamemode=creative
        motd=§a{{ project_name }} §4(beet)§r\n{{ project_directory | replace("\\", "\\\\") }}
    """


@dataclass
class PlaygroundArgs:
    java: Path
    server_jar: Path
    server_properties: str
    port: int | None


def bootstrap(ctx: Context):
    playground = ctx.inject(Playground)
    playground.clean()

    ctx.require(start)

    autosave = ctx.inject(Autosave)
    if autosave.link:
        # Make sure these run after LinkManager.autosave_handler
        autosave.add_link(link)
        autosave.add_link(reload)
    else:
        autosave.add_output(link)
        autosave.add_output(reload)


@configurable("playground", validator=PlaygroundOptions)
def start(ctx: Context, opts: PlaygroundOptions):
    playground = ctx.inject(Playground)
    vanilla = ctx.inject(Vanilla).shared

    args = PlaygroundArgs(
        java=vanilla.java,
        server_jar=vanilla.server_jar.path,
        server_properties=dedent(ctx.template.render_string(opts.server_properties)),
        port=opts.port,
    )
    playground.start(args)


def stop(ctx: Context):
    playground = ctx.inject(Playground)
    playground.stop()


def link(ctx: Context):
    playground = ctx.inject(Playground)
    playground.link(ctx.data)


def reload(ctx: Context):
    playground = ctx.inject(Playground)
    playground.server.exec("reload")


class Playground:
    server: ServerThread
    external_world: Path | None

    cache: Cache
    dirty = CachePin[list[str]]("dirty", default_factory=list)

    def __init__(
        self,
        arg: Context | MultiCache[Cache] | Cache,
        *,
        server: ServerThread | None = None,
        external_world: FileSystemPath | None = None,
    ):
        if server is not None:
            self.server = server
        elif isinstance(arg, Context):
            with arg.worker(playground_worker) as channel:
                self.server = channel.recv()
        else:
            raise ValueError("Server not provided.")

        if isinstance(arg, Context):
            arg = arg.cache

        if external_world is None and isinstance(arg, MultiCache):
            external_world = LinkManager(arg).world
        if external_world is not None:
            external_world = Path(external_world).resolve()

        self.external_world = external_world

        if isinstance(arg, MultiCache):
            arg = arg["playground"]

        self.cache = arg

    def start(self, args: PlaygroundArgs):
        if self.external_world and self.external_world.is_dir():
            world = str(self.external_world).replace("\\", "\\\\")
        else:
            world = "world"
        args.server_properties += f"\nlevel-name={world}\n"

        if self.server.args == args:
            return

        if self.server.started.is_set():
            self.stop()

        universe = self.cache.directory
        self.server.queue.put((universe, args))
        self.server.started.wait()

    def stop(self):
        try:
            self.server.exec("stop")
            self.server.stopped.wait()
        except PlaygroundNotStarted:
            pass

    def link(self, data: DataPack):
        try:
            world = self.external_world or self.cache.directory / "world"
            path = data.save(world / "datapacks")
        except PackOverwrite:
            return
        if self.cache.directory in path.parents:
            path = "/".join(path.relative_to(self.cache.directory).parts)
        self.dirty.append(str(path))

    def clean(self):
        remove_path(*[self.cache.directory / path for path in self.dirty])
        self.dirty.clear()


def playground_worker(connection: Connection[None, ServerThread]):
    server = ServerThread()
    server.start()

    for client in connection:
        client.send(server)
        client.close()

    try:
        server.exec("stop")
    except PlaygroundNotStarted:
        pass

    server.queue.join()


class ServerThread(Thread):
    queue: Queue[tuple[Path, PlaygroundArgs]]

    proc: subprocess.Popen[str] | None
    args: PlaygroundArgs | None

    started: Event
    ready: Event
    stopped: Event

    logger: logging.Logger
    listeners: list[Queue[str]]

    def __init__(self) -> None:
        super().__init__(daemon=True)
        self.queue = Queue()

        self.proc = None
        self.args = None

        self.started = Event()
        self.ready = Event()
        self.stopped = Event()
        self.stopped.set()

        self.logger = logging.getLogger("game")
        self.listeners = []

    def run(self):
        self.logger.addFilter(_filter_game_log)
        while True:
            universe, args = self.queue.get()
            self.loop(universe, args)
            self.queue.task_done()

    def loop(self, universe: Path, args: PlaygroundArgs):
        self.stopped.clear()

        args.server_jar.with_name("eula.txt").write_text("eula=true\n")
        args.server_jar.with_name("server.properties").write_text(
            args.server_properties,
            encoding="utf-8",
        )

        cmd = [args.java, "-jar", args.server_jar, "--nogui"]
        cmd += ["--universe", universe]
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

        self.started.set()

        regex = re.compile(r"\[(.+?)\] \[.+?/(DEBUG|INFO|WARN|ERROR|FATAL)\]: (.+)")
        previous_level = ""

        assert self.proc.stdout
        for line in self.proc.stdout:
            for queue in self.listeners:
                queue.put(line)

            extra = {}

            if m := regex.match(line):
                level = m[2]
                message = m[3]
                if message.startswith("Done ("):
                    self.ready.set()
            else:
                level = previous_level
                message = line
                extra["continue"] = True

            if level == "DEBUG":
                self.logger.debug(message, extra=extra)
            elif level == "INFO":
                self.logger.info(message, extra=extra)
            elif level == "WARN":
                self.logger.warning(message, extra=extra)
            elif level in ["ERROR", "FATAL"]:
                self.logger.error(message, extra=extra)

            previous_level = level

        self.proc.wait()
        self.proc = None
        self.args = None

        self.started.clear()
        self.ready.clear()
        self.stopped.set()

    def exec(self, command: str):
        if self.stopped.is_set():
            raise PlaygroundNotStarted()
        self.ready.wait()
        proc = self.proc
        assert proc
        assert proc.stdin
        proc.stdin.write(command + "\n")
        proc.stdin.flush()

    @contextmanager
    def listen(self, timeout: float | None = None) -> Generator[Iterator[str]]:
        queue: Queue[str] = Queue()
        self.listeners.append(queue)
        try:
            yield _drain_queue(queue, timeout=timeout)
        finally:
            self.listeners.remove(queue)
            queue.shutdown()


def _drain_queue[T](queue: Queue[T], timeout: float | None = None) -> Iterator[T]:
    while True:
        try:
            yield queue.get(timeout=timeout)
        except ShutDown, Empty:
            break


def _filter_game_log(record: logging.LogRecord) -> bool:
    record.msg = record.getMessage().removeprefix("[Not Secure] ")
    return True
