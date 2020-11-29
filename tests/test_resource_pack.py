from pathlib import Path
from typing import Any

import pytest
from PIL import Image, ImageDraw

from beet import ResourcePack, Texture


def test_default():
    assert ResourcePack() == ResourcePack()
    assert ResourcePack().empty


@pytest.mark.parametrize(  # type: ignore
    "pack",
    [
        ResourcePack("p1"),
        ResourcePack("p2", mcmeta={"pack": {"description": "world"}}),
        ResourcePack(
            "p3", mcmeta={"pack": {"description": "world", "pack_format": 42}}
        ),
    ],
)
def test_empty(snapshot: Any, pack: ResourcePack):
    assert snapshot("resource_pack") == pack
    assert pack.empty
    assert dict(pack) == {}


def test_empty_namespaces():
    pack = ResourcePack()

    assert not pack
    assert pack.empty

    assert pack["hello"]
    assert pack["hello"].empty

    assert pack["world"]
    assert pack["world"].empty

    assert pack
    assert pack.empty


def test_texture(snapshot: Any):
    image = Image.new("RGB", (64, 64))
    d = ImageDraw.Draw(image)
    d.text((10, 10), "hello", fill="white")

    pack = ResourcePack("custom")
    pack["custom:hello"] = Texture(image)

    assert snapshot("resource_pack") == pack


def test_texture_mcmeta(snapshot: Any):
    image = Image.new("RGB", (64, 128))
    d = ImageDraw.Draw(image)
    d.text((10, 10), "hello", fill="white")
    d.text((10, 74), "world", fill="white")

    pack = ResourcePack("custom")
    pack["custom:hello"] = Texture(image, mcmeta={"animation": {"frametime": 20}})

    assert snapshot("resource_pack") == pack


def test_merge(snapshot: Any):
    p1 = ResourcePack("p1")
    p1["custom:red"] = Texture(Image.new("RGB", (32, 32), color="red"))

    p2 = ResourcePack("p2")
    p2["custom:green"] = Texture(Image.new("RGB", (32, 32), color="green"))

    blink = Image.new("RGB", (32, 64), color="blue")
    d = ImageDraw.Draw(blink)
    d.rectangle([0, 32, 32, 64], fill="white")

    p3 = ResourcePack("p3")
    p3["other:blue"] = Texture(blink, mcmeta={"animation": {"frametime": 20}})

    p1.merge(p2)
    p1.merge(p3)

    assert snapshot("resource_pack") == p1


def test_vanilla_compare(minecraft_resource_pack: Path):
    assert ResourcePack(path=minecraft_resource_pack) == ResourcePack(
        path=minecraft_resource_pack
    )


def test_vanilla_zip(minecraft_resource_pack: Path, tmp_path: Path):
    pack = ResourcePack(path=minecraft_resource_pack)
    zipped_pack = pack.dump(tmp_path, zipped=True)
    assert ResourcePack(path=zipped_pack) == ResourcePack(path=zipped_pack)
