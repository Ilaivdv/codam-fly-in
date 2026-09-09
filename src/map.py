from enum import StrEnum


class ZoneType(StrEnum):
    START = "start_hub"
    HUB = "hub"
    END = "end_hub"


class ZoneRule(StrEnum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Map:
    def __init__(self) -> None:
        self.nb_drones: int
        self.zones: dict[str, Zone] = {}


class Zone:
    def __init__(self, type: str, coords: tuple[int, ...]) -> None:
        self.type: ZoneType = ZoneType(type)
        self.connections: list[tuple[Zone, int]] = []
        self.coords: tuple[int, ...] = coords
        self.rule: ZoneRule = ZoneRule.NORMAL
        self.color: str = ""  # TODO Find a way to cleanly implement colors
