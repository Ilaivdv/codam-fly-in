import pytest
from src.config.map_settings import MapValidator, MapError

def test_invalid() -> None:
    map = MapValidator()

    with pytest.raises(MapError):
        map.validate_map("fake_directory/a.tx")

    with pytest.raises(MapError):
        map.validate_map("unit_test/maps/invalid00.txt")

    with pytest.raises(MapError):
        map.validate_map("unit_test/maps/invalid01.txt")

    with pytest.raises(MapError):
        map.validate_map("unit_test/maps/invalid02.txt")


def test_valid() -> None:
    map = MapValidator()

    map.validate_map("unit_test/maps/valid00.txt")

