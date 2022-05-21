"""Service for linking the project to Minecraft."""


__all__ = [
    "LinkManager",
]


import logging
import os
import platform
from pathlib import Path
from typing import List, Optional, Union

from beet import Cache, CachePin, Context, ErrorMessage, MultiCache, PackOverwrite
from beet.core.utils import FileSystemPath, log_time, remove_path

logger = logging.getLogger("link")


def link_cache_finalizer(cache: Cache):
    """Link cache finalizer."""
    LinkManager(cache).clean()


class LinkManager:
    cache: Cache

    dirty = CachePin[List[str]]("dirty", default_factory=list)

    world = CachePin[Optional[str]]("world", None)
    minecraft = CachePin[Optional[str]]("minecraft", None)
    data_pack = CachePin[Optional[str]]("data_pack", None)
    resource_pack = CachePin[Optional[str]]("resource_pack", None)

    def __init__(self, arg: Union[Context, MultiCache[Cache], Cache]):
        if isinstance(arg, Context):
            arg = arg.cache
        if isinstance(arg, MultiCache):
            arg = arg["link"]
        self.cache = arg
        self.cache.add_finalizer(link_cache_finalizer)

    def clean(self):
        """Remove the previously linked files and folders."""
        remove_path(*self.dirty)
        self.dirty.clear()

    def autosave_handler(self, ctx: Context):
        """Plugin for linking the generated resource pack and data pack to Minecraft."""
        to_link = [
            (Path(directory), pack)
            for directory, pack in zip([self.resource_pack, self.data_pack], ctx.packs)
            if directory and pack
        ]

        if to_link:
            with log_time("Link project."):
                for directory, pack in to_link:
                    try:
                        self.dirty.append(str(pack.save(directory)))
                    except PackOverwrite as exc:
                        logger.warning(
                            f"Remove the conflicting pack to set up the link. {exc}"
                        )

    def setup_link(
        self,
        world: Optional[FileSystemPath] = None,
        minecraft: Optional[FileSystemPath] = None,
        data_pack: Optional[FileSystemPath] = None,
        resource_pack: Optional[FileSystemPath] = None,
    ):
        """Associate minecraft directories to the project."""
        if minecraft:
            minecraft = Path(minecraft).resolve()
            if not minecraft.is_dir():
                raise ErrorMessage(f"The specified Minecraft folder does not exist.")
        else:
            self.locate_minecraft()
            minecraft = Path(self.minecraft) if self.minecraft else None

        if world:
            world_name = world
            world = Path(world).resolve()
            if not (world / "level.dat").is_file():
                if minecraft and Path(world_name).parts == (world_name,):
                    world = minecraft / "saves" / world_name
                    if not world.is_dir():
                        raise ErrorMessage(
                            f"Couldn't find {str(world_name)!r} in the Minecraft save folder."
                        )
                else:
                    raise ErrorMessage(f"The specified world folder is invalid.")
        else:
            world = None

        if data_pack:
            data_pack = Path(data_pack).resolve()
            if not data_pack.is_dir():
                raise ErrorMessage(
                    f"The specified data packs directory does not exist."
                )
        elif world:
            data_pack = world / "datapacks"
        else:
            data_pack = None

        if data_pack and not world:
            world = data_pack.parent
        if world and not minecraft:
            minecraft = world.parent.parent

        if resource_pack:
            resource_pack = Path(resource_pack).resolve()
            if not resource_pack.is_dir():
                raise ErrorMessage(
                    f"The specified resource packs directory does not exist."
                )
        elif minecraft:
            resource_pack = minecraft / "resourcepacks"
        else:
            resource_pack = None

        if resource_pack and not minecraft:
            minecraft = resource_pack.parent

        if world:
            self.world = str(world)
        if minecraft:
            self.minecraft = str(minecraft)
        if data_pack:
            self.data_pack = str(data_pack)
        if resource_pack:
            self.resource_pack = str(resource_pack)

    def clear_link(self):
        """Clear the link."""
        self.cache.clear()

    def locate_minecraft(self):
        """Try to find the .minecraft folder."""
        locations = [
            Path(path)
            for path in os.environ.get("MINECRAFT_PATH", "").split(":")
            if path
        ]
        system = platform.system()

        if system == "Linux":
            locations.append(Path("~/.minecraft").expanduser())
            locations.append(
                Path("~/.var/app/com.mojang.Minecraft/data/minecraft").expanduser()
            )
        elif system == "Darwin":
            locations.append(
                Path("~/Library/Application Support/minecraft").expanduser()
            )
        elif system == "Windows":
            locations.append(Path(os.path.expandvars(r"%APPDATA%\.minecraft")))

        if path := next((path for path in locations if path and path.is_dir()), None):
            self.minecraft = str(path.resolve())

    def summary(self) -> str:
        """Return a formatted summary."""
        return "\n".join(
            f"{title}:\n  |  directory = {directory}\n"
            for title, directory in [
                ("Minecraft installation", self.minecraft),
                ("World folder", self.world),
                ("Data packs directory", self.data_pack),
                ("Resource packs directory", self.resource_pack),
            ]
        )
