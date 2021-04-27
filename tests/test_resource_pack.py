from pathlib import Path

import pytest
from PIL import Image, ImageDraw
from pytest_insta import SnapshotFixture

from beet import JsonFile, PngFile, ResourcePack, Sound, SoundConfig, Texture


def test_default():
    assert ResourcePack() == ResourcePack()
    assert not ResourcePack()


@pytest.mark.parametrize(  # type: ignore
    "pack",
    [
        ResourcePack("p1"),
        ResourcePack("p2", mcmeta=JsonFile({"pack": {"description": "world"}})),
        ResourcePack(
            "p3", mcmeta=JsonFile({"pack": {"description": "world", "pack_format": 42}})
        ),
    ],
)
def test_empty(snapshot: SnapshotFixture, pack: ResourcePack):
    assert snapshot("resource_pack") == pack
    assert not pack
    assert dict(pack) == {}


def test_empty_with_image():
    pack = ResourcePack(image=PngFile(Image.new("RGB", (32, 32), color="blue")))
    assert pack
    assert pack == ResourcePack(image=PngFile(Image.new("RGB", (32, 32), color="blue")))
    assert pack != ResourcePack(image=PngFile(Image.new("RGB", (32, 32), color="red")))
    assert pack != ResourcePack(image=PngFile(Image.new("RGB", (16, 16), color="blue")))
    assert dict(pack) == {}


def test_empty_namespaces():
    pack = ResourcePack()

    assert not pack
    assert not pack["hello"]
    assert not pack["world"]


def test_mcmeta_properties():
    pack = ResourcePack()
    pack.description = "Something"
    pack.pack_format = 1

    assert pack.mcmeta.content == {
        "pack": {"description": "Something", "pack_format": 1}
    }


def test_texture(snapshot: SnapshotFixture):
    image = Image.new("RGB", (64, 64))
    d = ImageDraw.Draw(image)
    d.text((10, 10), "hello", fill="white")

    pack = ResourcePack("custom")
    pack["custom:hello"] = Texture(image)

    assert snapshot("resource_pack") == pack


def test_texture_mcmeta(snapshot: SnapshotFixture):
    image = Image.new("RGB", (64, 128))
    d = ImageDraw.Draw(image)
    d.text((10, 10), "hello", fill="white")
    d.text((10, 74), "world", fill="white")

    pack = ResourcePack("custom")
    pack["custom:hello"] = Texture(image, mcmeta={"animation": {"frametime": 20}})

    assert snapshot("resource_pack") == pack


def test_sounds():
    pack = ResourcePack()
    pack["minecraft:block/note_block/banjo_1"] = Sound(
        b"abc", event="block.note_block.banjo", subtitle="foo"
    )
    pack["minecraft:block/note_block/banjo_2"] = Sound(
        b"123", event="block.note_block.banjo", weight=2, pitch=1.1
    )

    config = {
        "block.note_block.banjo": {
            "sounds": [
                "block/note_block/banjo_1",
                {"name": "block/note_block/banjo_2", "weight": 2, "pitch": 1.1},
            ],
            "subtitle": "foo",
        }
    }

    assert pack["minecraft"].sound_config == SoundConfig(config)


def test_merge(snapshot: SnapshotFixture):
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
    zipped_pack = pack.save(tmp_path, zipped=True)
    assert ResourcePack(path=zipped_pack) == ResourcePack(path=zipped_pack)


def test_vanilla_shaders(snapshot: SnapshotFixture, minecraft_resource_pack: Path):
    pack = ResourcePack(path=minecraft_resource_pack)
    assert snapshot("json") == pack.shader_posts["minecraft:spider"].data
    assert snapshot("json") == pack.shaders["minecraft:program/entity_outline"].data
    assert snapshot() == pack.fragment_shaders["minecraft:program/wobble"].text
    assert snapshot() == pack.vertex_shaders["minecraft:program/sobel"].text


def test_vanilla_particles(snapshot: SnapshotFixture, minecraft_resource_pack: Path):
    pack = ResourcePack(path=minecraft_resource_pack)
    assert snapshot("json") == pack.particles["minecraft:end_rod"].data
