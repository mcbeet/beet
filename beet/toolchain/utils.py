__all__ = [
    "locate_minecraft",
]


import os
import platform
from pathlib import Path
from typing import Optional


def locate_minecraft() -> Optional[Path]:
    path = None
    system = platform.system()

    if system == "Linux":
        path = Path("~/.minecraft").expanduser()
    elif system == "Darwin":
        path = Path("~/Library/Application Support/minecraft").expanduser()
    elif system == "Windows":
        path = Path(os.path.expandvars(r"%APPDATA%\.minecraft"))

    return path.resolve() if path and path.is_dir() else None
