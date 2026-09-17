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

        routes: list[list[Zone]] = [[self._end]]
        valid_routes: list[list[Zone]] = []
        while len(routes):
            for route in routes:
                branches: list[Zone] = route[-1].get_neighbors()
                for branch in branches:
                    if branch in route:
                        continue
                    new_route: list[Zone] = route.copy()
                    new_route.append(branch)
                    if branch.type is ZoneType.START:
                        valid_routes.append(new_route)
                    elif branch.get_neighbors():
                        routes.append(new_route)
                routes.remove(route)

        valid_routes.sort(key=len, reverse=True)
        for route in valid_routes:
            distance_from_end: int = 0
            for node in route:
                if node.distance > distance_from_end or node.distance <= -1:
                    node.distance = distance_from_end
                distance_from_end += 1

        ## DEBUG
        # for i in valid_routes:
        #     for j in i:
        #         print(f"{j.__str__()} distance: {j.distance}")
        #     print("\n")

    def get_start_end_zones(self) -> bool:
        for zone in self.zones.values():
            if zone.type is ZoneType.START:
                self._start = zone
            elif zone.type is ZoneType.END:
                self._end = zone
        return bool(self._start and self._end)


class Connection:
    def __init__(self, capacity: int, to_zone: Zone) -> None:
        self.capacity: int = capacity
        self.to: Zone = to_zone


class Zone:
    def __init__(self, type: str, pos: tuple[int, ...], parent: Map) -> None:
        self._map: Map = parent
        self.max_drones: int = 1
        self.color: str = "gray"

        self.connections: list[Connection] = []
        self.distance: int = -1

        self.type: ZoneType = ZoneType(type)
        self.rule: ZoneRule = ZoneRule.NORMAL
        self.pos: tuple[int, ...] = pos

    def __str__(self) -> str:
        return [k for k, v in self._map.zones.items() if v is self][0]

    def get_neighbors(self) -> list[Zone]:
        return [zone.to for zone in self.connections if zone.to is not self]


class Drone:
    def __init__(self, id: int) -> None:
        self._id: int = id
