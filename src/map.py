from src.zone import Zone, ZoneRule, ZoneType
from src.drone import Drone
from colorama import Fore


class MapError(Exception):
    """ Map error for verbosity """

    def __init__(self, msg: str) -> None:
        super().__init__(f"\n{Fore.RED}Error{Fore.RESET}: {msg}")


class Map:
    def __init__(self) -> None:
        self.nb_drones: int
        self.drones: dict[int, Drone] = {}
        self.zones: dict[str, Zone] = {}
        self._start: Zone
        self._end: Zone

    def init_drones(self, nb_drones: int) -> None:
        if not self.get_start_end_zones():
            raise MapError("couldn't get start and/or end zones")

        for i in range(1, nb_drones + 1):
            self.drones[i] = Drone(id=i, start_zone=self._start)

    def map_distances(self) -> None:
        # Go from end to start saving all routes that reach start_hub
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

        # Map distance to end on each zone overwriting if shorter one found
        for route in valid_routes:
            distance_from_end: int = 0
            for node in route:
                if node.distance > distance_from_end or node.distance <= -1:
                    node.distance = distance_from_end
                distance_from_end += 1

        # Add 1 to distance price for each zone that has RESTRICTED rule
        for zone in self.zones.values():
            zone.distance += bool(zone.rule is ZoneRule.RESTRICTED)

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
