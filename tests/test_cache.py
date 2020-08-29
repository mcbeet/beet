from time import sleep

from beet.cache import MultiCache, Cache


def test_cache(tmpdir):
    with Cache(tmpdir) as cache:
        cache.data["hello"] = "world"

    assert tmpdir.listdir() == [tmpdir / "index.json"]

    with Cache(tmpdir) as cache:
        assert cache.data["hello"] == "world"


def test_cache_directory(tmpdir):
    with Cache(tmpdir) as cache:
        hello = cache.directory / "hello.txt"
        hello.write_text("world")

    assert (tmpdir / "hello.txt").isfile()


def test_multi_cache(tmpdir):
    with MultiCache(tmpdir) as cache:
        cache["foo"].data["hello"] = "world"

    assert (tmpdir / "foo" / "index.json").isfile()

    with MultiCache(tmpdir) as cache:
        assert cache["foo"].data["hello"] == "world"


def test_default_multi_cache(tmpdir):
    with MultiCache(tmpdir) as cache:
        cache.data["hello"] = "world"

    assert (tmpdir / "default" / "index.json").isfile()

    with MultiCache(tmpdir) as cache:
        assert cache.data["hello"] == "world"
        assert cache["default"].data["hello"] == "world"


def test_default_multi_cache_directory(tmpdir):
    with MultiCache(tmpdir) as cache:
        hello = cache.directory / "hello.txt"
        hello.write_text("world")

    assert (tmpdir / "default" / "hello.txt").isfile()


def test_cache_expiration(tmpdir):
    with MultiCache(tmpdir) as cache:
        hello = cache.directory / "hello.txt"
        hello.write_text("world")
        cache["default"].timeout(milliseconds=200)

    sleep(0.1)

    with MultiCache(tmpdir) as cache:
        assert (cache.directory / "hello.txt").read_text() == "world"

    sleep(0.1)

    with MultiCache(tmpdir) as cache:
        assert cache["default"].expires is None
        assert not (cache.directory / "hello.txt").is_file()


def test_cache_refresh(tmpdir):
    with MultiCache(tmpdir) as cache:
        cache["foo"].timeout(milliseconds=200)
        assert cache["foo"].expires is not None

    sleep(0.1)

    with MultiCache(tmpdir) as cache:
        assert cache["foo"].expires is not None
        cache["foo"].restart_timeout()

    sleep(0.1)

    with MultiCache(tmpdir) as cache:
        assert cache["foo"].expires is not None

    sleep(0.1)

    with MultiCache(tmpdir) as cache:
        assert cache["foo"].expires is None


def test_cache_clear(tmpdir):
    with MultiCache(tmpdir) as cache:
        cache["foo"].data["hello"] = "world"
        assert len(tmpdir.listdir()) == 1
        cache.clear()
        assert len(cache) == 0
        assert tmpdir.listdir() == []


def test_cache_delete(tmpdir):
    with MultiCache(tmpdir / "cache") as cache:
        cache["foo"].data["hello"] = "world"
        assert len(tmpdir.listdir()) == 1
        cache.delete()
        assert len(cache) == 0
        assert tmpdir.listdir() == []


def test_cache_length(tmpdir):
    with MultiCache(tmpdir) as cache:
        cache["1"]
        cache["2"]
        assert len(cache) == 2
        assert len(tmpdir.listdir()) == 2

        del cache["1"]
        assert len(cache) == 1
        assert len(tmpdir.listdir()) == 1
