__all__ = [
    "format_obj",
    "format_exc",
    "import_from_string",
    "locate_minecraft",
]


import os
import platform
from importlib import import_module
from pathlib import Path
from traceback import format_exception
from typing import Any, Optional


def format_exc(exc: BaseException) -> str:
    return "".join(format_exception(exc.__class__, exc, exc.__traceback__))


def format_obj(obj: Any) -> str:
    module = getattr(obj, "__module__", None)
    name = getattr(obj, "__qualname__", None)
    return repr(f"{module}.{name}") if module and name else repr(obj)


def import_from_string(dotted_path: str, default_member: Optional[str] = None) -> Any:
    try:
        module = import_module(dotted_path)
    except ImportError:
        if "." not in dotted_path:
            raise

        dotted_path, _, default_member = dotted_path.rpartition(".")

        try:
            module = import_module(dotted_path)
        except Exception as exc:
            raise exc from None

    return getattr(module, default_member) if default_member else module


def locate_minecraft() -> Optional[Path]:
    locations = [
        Path(path) for path in os.environ.get("MINECRAFT_PATH", "").split(":") if path
    ]
    system = platform.system()

    if system == "Linux":
        locations.append(Path("~/.minecraft").expanduser())
        locations.append(
            Path("~/.var/app/com.mojang.Minecraft/data/minecraft").expanduser()
        )
    elif system == "Darwin":
        locations.append(Path("~/Library/Application Support/minecraft").expanduser())
    elif system == "Windows":
        locations.append(Path(os.path.expandvars(r"%APPDATA%\.minecraft")))

    return next((path.resolve() for path in locations if path and path.is_dir()), None)
