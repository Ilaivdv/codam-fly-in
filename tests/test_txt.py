from src.parsing import MapValidator, ParseError
from src.map import MapError
import pytest

def test_invalid_metadata() -> None:
    map = MapValidator()

    with pytest.raises(ParseError):
        assert map.validate_map("tests/maps/invalid_connect_metadata.txt")

    with pytest.raises(ParseError):
        assert map.validate_map("tests/maps/invalid_zone_metadata.txt")

    with pytest.raises(ParseError):
        assert map.validate_map("tests/maps/invalid_duplicate_metadata.txt")


def test_invalid_numbers() -> None:
    map = MapValidator()

    with pytest.raises(ParseError):
        assert map.validate_map("tests/maps/invalid_0_drones.txt")

    with pytest.raises(ParseError):
        assert map.validate_map("tests/maps/invalid_coords.txt")

    with pytest.raises(ParseError):
        assert map.validate_map("tests/maps/invalid_argument_amount.txt")

    with pytest.raises(ParseError):
        assert map.validate_map("tests/maps/invalid_negative_drones.txt")

    with pytest.raises(ParseError):
        assert map.validate_map("tests/maps/invalid_negative_capacity.txt")

    with pytest.raises(ParseError):
        assert map.validate_map("tests/maps/invalid_zone_capacity.txt")

    with pytest.raises(ParseError):
        assert map.validate_map("tests/maps/invalid_connect_capacity.txt")

    with pytest.raises(MapError):
        assert map.validate_map("tests/maps/invalid_duplicate_coords.txt")


def test_invalid_config() -> None:
    map = MapValidator()

    with pytest.raises(ParseError):
        assert map.validate_map("tests/maps/invalid_unordered.txt")

    with pytest.raises(ParseError):
        assert map.validate_map("tests/maps/invalid_zone.txt")

    with pytest.raises(ParseError):
        assert map.validate_map("tests/maps/invalid_connect.txt")

    with pytest.raises(ParseError):
        assert map.validate_map("tests/maps/invalid_duplicate_connect.txt")

    with pytest.raises(ParseError):
        assert map.validate_map("tests/maps/invalid_text.txt")


def test_invalid_files() -> None:
    map = MapValidator()

    with pytest.raises(ParseError):
        assert map.validate_map("fake_directory/a.tx")

    with pytest.raises(ParseError):
        assert map.validate_map("tests/maps/invalid_empty.txt")

    with pytest.raises(ParseError):
        assert map.validate_map("/etc/sudoers")


def test_valid_config() -> None:
    map = MapValidator()

    assert map.validate_map("tests/maps/valid_small.txt") is not None
    assert map.validate_map("tests/maps/valid_small.txt") is not None
    assert map.validate_map("tests/maps/valid_unordered.txt") is not None
    assert map.validate_map("tests/maps/valid_big_nb_drones.txt") is not None
    assert map.validate_map("tests/maps/valid_0_capacity.txt") is not None

