from beet.library.data_pack import DataPack


def test_registry_data():
    assert DataPack.pack_format_registry.normalize_key("1.21") == (1, 21)
    assert DataPack.pack_format_registry.normalize_key("1.21.1") == (1, 21, 1)
    assert DataPack.pack_format_registry.normalize_key("1.21.x") == (1, 21, "x")

    assert DataPack.pack_format_registry.missing((1, 20, "x")) == 41
    assert DataPack.pack_format_registry.missing((1, 19, "x")) == 12

    assert DataPack.pack_format_registry.get((1, 21, 10)) == (88, 0)
    assert DataPack.pack_format_registry.get((1, 21, 9)) == (88, 0)

    assert DataPack.pack_format_registry.get((1, 20)) == 15
    assert DataPack.pack_format_registry.get((1, 18)) == 8
