from beet.resources.pack_format_registry import data_pack_format_registry


def test_registry_data():
    assert data_pack_format_registry.normalize_key("1.21") == (1, 21)
    assert data_pack_format_registry.normalize_key("1.21.1") == (1, 21, 1)
    assert data_pack_format_registry.normalize_key("1.21.x") == (1, 21, "x")

    assert data_pack_format_registry.missing((1, 20, "x")) == 41
    assert data_pack_format_registry.missing((1, 19, "x")) == 12
