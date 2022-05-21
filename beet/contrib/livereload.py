"""Plugin for automatically reloading the data pack after the build."""


__all__ = [
    "livereload",
    "create_livereload_data_pack",
    "livereload_server",
    "LogCallback",
    "LogWatcher",
]


import json
import logging
import re
import time
from pathlib import Path
from threading import Event, Thread
from typing import Any, Callable, List, Optional, Tuple, overload

from beet import Connection, Context, DataPack, Function, PackOverwrite
from beet.contrib.autosave import Autosave
from beet.contrib.link import LinkManager
from beet.core.utils import FileSystemPath, JsonDict, remove_path

logger = logging.getLogger("livereload")
logger.addFilter(
    lambda r: not r.getMessage().startswith(("Ambiguity between arguments", "[CHAT]"))
)


GAME_LOG_REGEX = re.compile(r"\[(.+?)\] \[.+?/(DEBUG|INFO|WARN|ERROR|FATAL)\]: (.+)")
LIVERELOAD_REGEX = re.compile(r"\[CHAT\] livereload - (Ready|Reloaded)")


def beet_default(ctx: Context):
    autosave = ctx.inject(Autosave)
    autosave.add_link(livereload)


def livereload(ctx: Context):
    link_manager = ctx.inject(LinkManager)
    if not link_manager.data_pack or not ctx.data:
        return

    data = create_livereload_data_pack()

    try:
        livereload_path = data.save(link_manager.data_pack)
    except PackOverwrite as exc:
        livereload_path = Path(exc.path)

    dirty_path = str(livereload_path)
    if dirty_path not in link_manager.dirty:
        link_manager.dirty.append(dirty_path)

    with ctx.worker(livereload_server) as channel:
        channel.send((link_manager.minecraft, livereload_path))


def create_livereload_data_pack() -> DataPack:
    data = DataPack("livereload")

    prefix = {"text": "livereload -", "color": "gray"}
    ready = ["", prefix, " ", {"text": "Ready", "color": "aqua"}]
    changes = ["", prefix, " ", {"text": f"Changes detected", "color": "aqua"}]
    reloaded = ["", prefix, " ", {"text": f"Reloaded", "color": "aqua"}]

    data["livereload:load"] = Function(
        [
            "schedule clear livereload:poll",
            "scoreboard objectives add livereload dummy",
            f"execute unless score delta livereload matches 1.. run tellraw @a {json.dumps(ready)}",
            f"execute if score delta livereload matches 1.. run tellraw @a {json.dumps(reloaded)}",
            "schedule function livereload:poll 1s",
        ],
        tags=["minecraft:load"],
    )

    data["livereload:poll"] = Function(
        [
            "execute store result score new_pack_count livereload run datapack list available",
            "scoreboard players operation delta livereload = new_pack_count livereload",
            "scoreboard players operation delta livereload -= pack_count livereload",
            "scoreboard players operation pack_count livereload = new_pack_count livereload",
            "execute unless score delta livereload matches 1.. run schedule function livereload:poll 1s",
            f"execute if score delta livereload matches 1.. run tellraw @a {json.dumps(changes)}",
            "execute if score delta livereload matches 1.. run schedule function livereload:reload 1s",
        ]
    )

    data["livereload:reload"] = Function(["reload"])

    return data


def livereload_server(connection: Connection[Tuple[Optional[str], Path], None]):
    minecraft_path = None
    livereload_path = None

    with LogWatcher() as log_watcher:
        for client in connection:
            for message in client:
                if message == (minecraft_path, livereload_path):
                    continue

                minecraft_path, livereload_path = message

                if not minecraft_path:
                    logger.warning(
                        "Not linked to any Minecraft installation. Reloading disabled."
                    )
                    continue

                log_file_path = Path(minecraft_path) / "logs" / "latest.log"

                if not log_file_path.is_file():
                    logger.warning("Couldn't find game log. Reloading disabled.")
                    continue

                @log_watcher.tail(log_file_path)
                def _(args: JsonDict):
                    if LIVERELOAD_REGEX.match(args["message"]) and livereload_path:
                        remove_path(livereload_path)


LogCallback = Callable[[JsonDict], Any]


class LogWatcher:
    event: Event
    thread: Optional[Thread]

    def __init__(self):
        self.event = Event()
        self.thread = None

    @overload
    def tail(self, path: FileSystemPath) -> Callable[[LogCallback], None]:
        ...

    @overload
    def tail(self, path: FileSystemPath, callback: LogCallback):
        ...

    def tail(
        self,
        path: FileSystemPath,
        callback: Optional[LogCallback] = None,
    ) -> Any:
        def decorator(callback: LogCallback):
            if self.thread:
                self.event.set()
                self.thread.join()
            self.event.clear()
            self.thread = Thread(target=self.target, args=(path, callback))
            self.thread.start()

        if callback:
            decorator(callback)
        else:
            return decorator

    def target(self, path: FileSystemPath, callback: LogCallback):
        queue: List[str] = []

        with open(path, "r", errors="ignore") as f:
            f.seek(0, 2)

            while not self.event.is_set():
                lines = f.read().splitlines()

                if queue and not lines:
                    self.handle_message(queue, callback)

                time.sleep(0.5)

                for line in lines:
                    if queue and line.startswith("["):
                        self.handle_message(queue, callback)
                    queue.append(line)

    def handle_message(self, queue: List[str], callback: LogCallback):
        message, *details = queue
        queue.clear()

        m = GAME_LOG_REGEX.match(message)

        if not m:
            return

        fmt = "%(message)s%(details)s"
        args = {
            "time": m[1],
            "level": m[2],
            "message": m[3],
            "details": "".join(f"\n{line}" for line in details),
        }

        if args["level"] == "DEBUG":
            logger.debug(fmt, args)
        elif args["level"] == "INFO":
            logger.info(fmt, args)
        elif args["level"] == "WARN":
            logger.warning(fmt, args)
        elif args["level"] in ["ERROR", "FATAL"]:
            logger.error(fmt, args)

        callback(args)

    def close(self):
        if self.thread:
            self.event.set()
            self.thread.join()

    def __enter__(self) -> "LogWatcher":
        return self

    def __exit__(self, *_):
        self.close()
