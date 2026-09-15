from colorama import Fore
from enum import StrEnum


class MapError(Exception):
    """ Map error for verbosity """

    def __init__(self, msg: str) -> None:
        super().__init__(f"\n{Fore.RED}Error{Fore.RESET}: {msg}")


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
        self._start: Zone
        self._end: Zone

    def init_drones(self, nb_drones: int) -> None:
        for i in range(1, nb_drones + 1):
            self.drones[i] = Drone(id=i)

    def map_distances(self) -> None:
        if not self.get_start_end_zones():
            raise MapError("couldn't get start and or end zones")

        routes: list[list[Zone]] = [[self._start]]
        while (len(routes)):
            for route in routes:
                head: Zone = route[-1]
                branches: list[Zone] = head.get_neighbors()
                for branch in branches:
                    new_route = route.copy().append(branch)

    def get_start_end_zones(self) -> bool:
        if not self._start and not self._end:
            for zone in self.zones.values():
                if zone.type is ZoneType.START:
                    self._start = zone
                elif zone.type is ZoneType.END:
                    self._end = zone
        return bool(self._start and self._end)



class Connection:
    def __init__(self, path: tuple[Zone, Zone], capacity: int) -> None:
        self.path: tuple[Zone, Zone] = path
        self.capacity: int = capacity


class Zone:
    def __init__(self, type: str, pos: tuple[int, ...]) -> None:
        self.connections: list[Connection] = []
        self.type: ZoneType = ZoneType(type)
        self.pos: tuple[int, ...] = pos
        self.rule: ZoneRule = ZoneRule.NORMAL
        self.color: str = "gray"
        self.max_drones: int = 1

        self.distance: int  # TODO Implement distance to end_hub

    def get_neighbors(self) -> list[Zone]:
        return [zone.path[1] for zone in self.connections]


class Drone:

    ## TODO Write pathfinding like a reverse dijkstra, from end to start
    ## Saving the distances to end hub whithin the zones
    def __init__(self, id: int) -> None:
        self._id: int = id
