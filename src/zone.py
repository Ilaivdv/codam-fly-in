from enum import StrEnum


class ZoneTypes(StrEnum):
    START = "start_hub"
    HUB = "hub"
    END = "end_hub"


class ZoneRules(StrEnum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Connection:
    def __init__(self, capacity: int, to_zone: Zone) -> None:
        self.capacity: int = capacity
        self.to: Zone = to_zone


class Zone:
    def __init__(self, name: str, type: str, pos: tuple[int, ...]) -> None:
        self.name: str = name
        self.max_drones: int = 1
        self.color: str = "gray"

        self.connections: list[Connection] = []
        self.distance: int = -1

        self.type: ZoneTypes = ZoneTypes(type)
        self.rule: ZoneRules = ZoneRules.NORMAL
        self.pos: tuple[int, ...] = pos

    def __str__(self) -> str:
        return self.name

    def get_neighbors(self) -> list[Zone]:
        return [zone.to for zone in self.connections if zone.to is not self]
