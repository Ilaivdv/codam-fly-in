from src.node import Zone, ZoneRules, ZoneTypes, Connection
from src.drone import Drone
from src.utils import Logs
from colorama import Fore


class MapError(Exception):
    """ Map error for verbosity """

    def __init__(self, msg: str) -> None:
        super().__init__(f"\n{Fore.RED}MapError{Fore.RESET}: {msg}")


class Map:
    def __init__(self, logs: Logs) -> None:
        self.nb_drones: int
        self.drones: dict[int, Drone] = {}

        self.zones: dict[str, Zone] = {}
        self._start: Zone
        self._end: Zone

        self.is_finished: bool = False
        self.logs: Logs = logs

    def validate_positions(self) -> None:
        zones_pos: list[tuple[int, int]] = []
        for k, v in self.zones.items():
            if v.pos in zones_pos:
                raise MapError((f"zone '{k.__str__()}' is overlapping with "
                                f"another zone at position: {v.pos}"))
            else:
                zones_pos.append(v.pos)

    def init_level(self) -> None:
        if not self._init_start_end_zones():
            raise MapError("couldn't get start and/or end zones")

        for i in range(1, self.nb_drones + 1):
            self.drones[i] = Drone(id=i, start_zone=self._start, log=self.logs)
        self._start.drone_amount = self.nb_drones
        self.map_distances()

    def _init_start_end_zones(self) -> bool:
        for zone in self.zones.values():
            if zone.type is ZoneTypes.START:
                zone.max_drones = self.nb_drones
                self._start = zone
            elif zone.type is ZoneTypes.END:
                zone.max_drones = self.nb_drones
                self._end = zone
        return bool(self._start and self._end)

    def map_distances(self) -> None:
        # Go from end to start saving all routes that reach start_hub
        routes: list[list[Zone]] = [[self._end]]
        valid_routes: list[list[Zone]] = []
        while len(routes):
            for route in routes:
                neighbors: list[Connection] = [i for i in
                                               route[-1].get_neighbors() if
                                               type(i) is Connection]
                branches: list[Zone] = [i.get_current_zone() for i in
                                        neighbors if i.is_behind]

                for branch in branches:
                    if branch in route or branch.rule is ZoneRules.BLOCKED:
                        continue
                    new_route: list[Zone] = route.copy()
                    new_route.append(branch)
                    if branch.type is ZoneTypes.START:
                        valid_routes.append(new_route)
                    elif branch.get_neighbors():
                        routes.append(new_route)
                routes.remove(route)

        if not len(valid_routes):
            raise MapError("No available routes from start_hub to end_hub")

        # Maps shortest distance from each zone to end and add zones to set
        valid_zones: set[Zone] = set()

        for route in valid_routes:
            distance_from_end: int = 0
            for node in route:
                if node.distance > distance_from_end or node.distance <= -1:
                    node.distance = distance_from_end
                    valid_zones.add(node)
                distance_from_end += 1

        # Add 1 to distance point for each restricted zone and add distances
        # to connections as well
        for zone in self.zones.values():
            zone.distance += bool(zone.rule is ZoneRules.RESTRICTED)
            zone.valid_zones = valid_zones
            for connection in zone.connections:
                connection.distance = connection.to.distance

            self.logs.log_debug(f"{zone.__str__()} distance: {zone.distance}")

    def advance_turn(self) -> None:
        # Process every drones move one by one
        for drone in self.drones.values():
            drone.current_state.on_event()
        self.logs.end_turn()

        # Check if all drones are done at the end of each turn
        self.is_finished = all([i.current_state is i.states["finished"]
                                for i in self.drones.values()])
