from beet.contrib.vanilla import Vanilla
from beet.contrib.unknown_files import UnknownAsset, UnknownData
import tempfile

from beet.core.cache import Cache
from beet.library.base import LATEST_MINECRAFT_VERSION
from beet.toolchain.helpers import run_beet
from zipfile import ZipFile
import sys


def main(version: str = LATEST_MINECRAFT_VERSION):
    # Test that all namespaces are known
    # It loads the vanilla jar and checks
    # that there are no unknown namespaces
    with tempfile.TemporaryDirectory() as dir:
        cache = Cache(dir)
        vanilla = Vanilla(cache=cache, minecraft_version=version)
        client_jar = vanilla.mount()
        with run_beet(
            {
                "require": ["beet.contrib.unknown_files"],
                "output": "build",
            },
        ) as ctx:
            # We loads directly from the jar file
            ctx.data.load(ZipFile(client_jar.path))
            ctx.assets.load(ZipFile(client_jar.path))

            known_assets: set[str] = {
                "minecraft:gpu_warnlist.json",
                "minecraft:regional_compliancies.json",
            }
            unknown_assets: list[str] = []
            for x in ctx.assets[UnknownAsset].keys():
                if x in known_assets:
                    continue
                unknown_assets.append(x)
            if unknown_assets:
                raise ValueError(
                    f"An unknown asset has no NamespaceFileType: {unknown_assets}"
                )

            known_data: set[str] = set()
            unknown_data: list[str] = []
            for x in ctx.data[UnknownData].keys():
                if x in known_data:
                    continue
                if x.startswith("minecraft:datapacks/"):
                    # We ignore datapacks
                    continue
                unknown_data.append(x)
            if unknown_data:
                raise ValueError(
                    f"An unknown data has no NamespaceFileType: {unknown_data}"
                )


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print("Usage : `python tests/test_scopes.py 1.21.4`")
