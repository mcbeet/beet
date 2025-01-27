"""Plugin that builds a MCBuild project."""

__all__ = ["beet_default", "MCBuildOptions"]


from typing import Optional, Any
from beet import Context, configurable
from pydantic.v1 import BaseModel
from beet.core.utils import FileSystemPath
import subprocess, shutil, json, requests, colorama, hashlib
from pathlib import Path


DEFAULT_CONFIG_URL = "https://raw.githubusercontent.com/mc-build/mcb/refs/heads/main/template/mcb.config.js"
CONFIG_FILE = "mcb.config.js"
OG_PRINT = print


def log(message: str) -> None:
    """Print with a custom prefix."""
    OG_PRINT(
        f"{colorama.Fore.LIGHTBLACK_EX}[{colorama.Fore.GREEN}MCB{colorama.Fore.WHITE}-{colorama.Fore.LIGHTRED_EX}BEET{colorama.Fore.LIGHTBLACK_EX}]{colorama.Fore.RESET}",
        message,
    )


def create_default_config(ctx: Context):
    res = requests.get(DEFAULT_CONFIG_URL)
    res.raise_for_status()

    with open(ctx.directory / CONFIG_FILE, "wb") as f:
        f.write(res.content)


def create_source_hash(source: Path, config: Path) -> str:
    hasher = hashlib.sha256()

    def update_from_file(path: Path):
        assert path.is_file()
        hasher.update(path.as_posix().encode())
        hasher.update(path.read_bytes())
        with open(path, "rb") as f:
            hasher.update(f.read())

    def update_from_directory(path: Path):
        assert path.is_dir()
        hasher.update(path.as_posix().encode())
        for path in sorted(path.iterdir()):
            if path.is_file():
                update_from_file(path)
            elif path.is_dir():
                update_from_directory(path)

    update_from_file(config)

    if source.is_file():
        update_from_file(source)
    elif source.is_dir():
        update_from_directory(source)

    return hasher.hexdigest()


class MCBuildOptions(BaseModel):
    force_rebuild: bool = False
    source: FileSystemPath = "./mcbuild"


def beet_default(ctx: Context):
    ctx.require(mcbuild)


@configurable(validator=MCBuildOptions)
def mcbuild(ctx: Context, opts: MCBuildOptions):
    config = ctx.directory / CONFIG_FILE
    source = ctx.directory / opts.source
    build_dir = ctx.cache["mcbuild"].directory / "datapack"
    previous_source_hash = ctx.cache["mcbuild"].json.get("source_hash", None)

    # Create default config if it doesn't exist
    if not config.exists():
        log("Default config not found, creating one...")
        create_default_config(ctx)

    source_hash = create_source_hash(source, config)

    # Check if source has changed
    if not opts.force_rebuild and source_hash == previous_source_hash:
        # If the build directory doesn't exist, then somehow the cache was lost. We need to rebuild.
        if (build_dir / "data").exists():
            # Load the cached datapack
            ctx.data.load(build_dir)
            return

    # Clear previous build
    shutil.rmtree(build_dir, ignore_errors=True)
    # Copy source
    shutil.copytree(source, build_dir / "src", dirs_exist_ok=True)
    # Copy config
    shutil.copy(config, build_dir / CONFIG_FILE)
    # Create dummy pack.mcmeta
    with open(build_dir / "pack.mcmeta", "w") as f:
        meta = {"pack": {"pack_format": ctx.data.pack_format}}
        json.dump(meta, f)
    # Run mcb
    command = ["mcb", "build"]
    try:
        subprocess.run(
            command, cwd=build_dir, check=True, capture_output=True, shell=True
        )
    except subprocess.CalledProcessError as e:
        log(f"Error while running MCB: {e.stderr.decode()}")

    # Load the built datapack
    ctx.data.load(build_dir)

    # Update source hash
    ctx.cache["mcbuild"].json["source_hash"] = source_hash
