from pathlib import Path
from time import sleep

from beet.core.cache import Cache, MultiCache


def test_cache(tmp_path: Path):
    with Cache(tmp_path) as cache:
        cache.json["hello"] = "world"

    assert list(tmp_path.iterdir()) == [tmp_path / "index.json"]

    with Cache(tmp_path) as cache:
        assert cache.json["hello"] == "world"

    with Cache(tmp_path) as cache:
        cache.json = {"foo": "bar"}

    with Cache(tmp_path) as cache:
        assert cache.json == {"foo": "bar"}


def test_cache_directory(tmp_path: Path):
    with Cache(tmp_path) as cache:
        hello = cache.directory / "hello.txt"
        hello.write_text("world")

    assert (tmp_path / "hello.txt").is_file()


def test_cache_get_path(tmp_path: Path):
    with Cache(tmp_path) as cache:
        path = cache.get_path(f"foo{id(cache)}")
        assert path == cache.directory / "0x0"

        for i in range(15):
            cache.get_path(f"{i}")

        assert cache.get_path("1") == cache.directory / "0x2"
        assert cache.get_path("") == cache.directory / "0x10"


def test_cache_get_path_extension(tmp_path: Path):
    with Cache(tmp_path) as cache:
        assert cache.get_path(".json").name == "0x0.json"
        assert cache.get_path(".json").name == "0x0.json"
        assert cache.get_path("\\^&~}#[|`\\^@]}{.json").name == "0x1.json"
        assert cache.get_path("\\^&~}#.[|`\\.^@]}{.png").name == "0x2.png"
        assert cache.get_path("\\^&~}#.[|`\\.^@]}{.txt").name == "0x3.txt"
        assert cache.get_path(".").name == "0x4"


def test_multi_cache(tmp_path: Path):
    with MultiCache(tmp_path) as cache:
        cache["foo"].json["hello"] = "world"

    assert (tmp_path / "foo" / "index.json").is_file()

    with MultiCache(tmp_path) as cache:
        assert cache["foo"].json["hello"] == "world"


def test_default_multi_cache(tmp_path: Path):
    with MultiCache(tmp_path) as cache:
        cache.json["hello"] = "world"

    assert (tmp_path / "default" / "index.json").is_file()

    with MultiCache(tmp_path) as cache:
        assert cache.json["hello"] == "world"
        assert cache["default"].json["hello"] == "world"


def test_default_multi_cache_directory(tmp_path: Path):
    with MultiCache(tmp_path) as cache:
        hello = cache.directory / "hello.txt"
        hello.write_text("world")

    assert (tmp_path / "default" / "hello.txt").is_file()


def test_cache_expiration(tmp_path: Path):
    with MultiCache(tmp_path) as cache:
        hello = cache.directory / "hello.txt"
        hello.write_text("world")
        cache["default"].timeout(milliseconds=200)

    sleep(0.1)

    with MultiCache(tmp_path) as cache:
        assert (cache.directory / "hello.txt").read_text() == "world"

    sleep(0.1)

    with MultiCache(tmp_path) as cache:
        assert cache["default"].expire is None
        assert not (cache.directory / "hello.txt").is_file()


def test_cache_refresh(tmp_path: Path):
    with MultiCache(tmp_path) as cache:
        cache["foo"].timeout(milliseconds=200)
        assert cache["foo"].expire is not None

    sleep(0.1)

    with MultiCache(tmp_path) as cache:
        assert cache["foo"].expire is not None
        cache["foo"].restart_timeout()

    sleep(0.1)

    with MultiCache(tmp_path) as cache:
        assert cache["foo"].expire is not None

    sleep(0.1)

    with MultiCache(tmp_path) as cache:
        assert cache["foo"].expire is None


def test_cache_clear(tmp_path: Path):
    with MultiCache(tmp_path / "cache") as cache:
        cache["foo"].json["hello"] = "world"
        assert len(list(tmp_path.iterdir())) == 1
        cache.clear()
        assert len(cache) == 0
        assert list(tmp_path.iterdir()) == []


def test_cache_length(tmp_path: Path):
    with MultiCache(tmp_path) as cache:
        assert cache["1"]
        assert cache["2"]
        assert len(cache) == 2
        assert len(list(tmp_path.iterdir())) == 2

        del cache["1"]
        assert len(cache) == 1
        assert len(list(tmp_path.iterdir())) == 1


def test_preload(tmp_path: Path):
    with MultiCache(tmp_path) as cache:
        cache["foo"].json["bar"] = 42

    with MultiCache(tmp_path) as cache:
        assert not cache
        cache.preload()
        assert cache.keys() == {"foo"}


def test_match(tmp_path: Path):
    with MultiCache(tmp_path) as cache:
        cache["test-foo"]
        cache["test-bar"]
        cache["other-hello"]
        assert cache.match("test-*") == {"test-foo", "test-bar"}
