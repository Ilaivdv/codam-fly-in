import pytest
from src.config.map_settings import MapValidator, MapError

def test_level_txt():
    map = MapValidator()
    # assert map.validate_map("unit_test/test0.txt")
    with pytest.raises(MapError) as excinfo:
        map.validate_map("unit_test/test0.txt")
