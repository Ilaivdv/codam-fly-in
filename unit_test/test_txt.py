import pytest
from src.config.map_settings import MapValidator, MapError

def test_invalid_config() -> None:
    map = MapValidator()

    with pytest.raises(MapError):
        assert map.validate_map("unit_test/maps/invalid_coords.txt")

    with pytest.raises(MapError):
        assert map.validate_map("unit_test/maps/invalid_connect_metadata.txt")

    with pytest.raises(MapError):
        assert map.validate_map("unit_test/maps/invalid_zone_metadata.txt")

    with pytest.raises(MapError):
        assert map.validate_map("unit_test/maps/invalid_text.txt")

    with pytest.raises(MapError):
        assert map.validate_map("unit_test/maps/invalid_unordered.txt")

    with pytest.raises(MapError):
        assert map.validate_map("unit_test/maps/invalid_connect.txt")

    with pytest.raises(MapError):
        assert map.validate_map("unit_test/maps/invalid_duplicate_connect.txt")

    with pytest.raises(MapError):
        assert map.validate_map("unit_test/maps/invalid_duplicate_metadata.txt")

    with pytest.raises(MapError):
        assert map.validate_map("unit_test/maps/invalid_zone.txt")


def test_invalid_files() -> None:
    map = MapValidator()

    with pytest.raises(MapError):
        assert map.validate_map("fake_directory/a.tx")

    with pytest.raises(MapError):
        assert map.validate_map("unit_test/maps/invalid_empty.txt")

    with pytest.raises(MapError):
        assert map.validate_map("/etc/sudoers")


def test_valid() -> None:
    map = MapValidator()

    assert map.validate_map("unit_test/maps/valid_small.txt") is not None
    assert map.validate_map("unit_test/maps/valid_small.txt") is not None

