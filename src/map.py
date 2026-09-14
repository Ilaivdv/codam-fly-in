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
        self.drones: dict[int, Drone] = {}
        self.zones: dict[str, Zone] = {}

    def init_drones(self, nb_drones: int) -> None:
        for i in range(1, nb_drones + 1):
            self.drones[i] = Drone(id=i)


class Zone:
    def __init__(self, type: str, coords: tuple[int, ...]) -> None:
        self.type: ZoneType = ZoneType(type)
        self.connections: list[tuple[Zone, int]] = []
        self.coords: tuple[int, ...] = coords
        self.rule: ZoneRule = ZoneRule.NORMAL
        self.color: str = "grey"
        self.max_drones: int = -1


class Drone:

    # TODO Write pathfinding like a reverse dijkstra, from end to start
    # Saving the distances to end hub whithin the zones
    def __init__(self, id: int) -> None:
        self._id: int = id
