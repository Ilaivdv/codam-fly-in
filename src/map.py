from src.zone import Zone, ZoneRules, ZoneTypes
from src.drone import Drone
from src.utils import Logs
from colorama import Fore


class MapError(Exception):
    """ Map error for verbosity """

    def __init__(self, msg: str) -> None:
        super().__init__(f"\n{Fore.RED}MapError{Fore.RESET}: {msg}")


class Map:
    def __init__(self) -> None:
        self.nb_drones: int
        self.drones: dict[int, Drone] = {}

        self.zones: dict[str, Zone] = {}
        self._start: Zone
        self._end: Zone

        self.is_finished: bool = False
        self.logs: Logs

    def _init_start_end_zones(self) -> bool:
        for zone in self.zones.values():
            if zone.type is ZoneTypes.START:
                zone.max_drones = self.nb_drones
                self._start = zone
            elif zone.type is ZoneTypes.END:
                zone.max_drones = self.nb_drones
                self._end = zone
        return bool(self._start and self._end)

    def init_drones(self, nb_drones: int) -> None:
        if not self._init_start_end_zones():
            raise MapError("couldn't get start and/or end zones")

        for i in range(1, nb_drones + 1):
            self.drones[i] = Drone(id=i, start_zone=self._start, log=self.logs)
        self._start.drone_amount = self.nb_drones

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
                    if branch.type is ZoneTypes.START:
                        valid_routes.append(new_route)
                    elif branch.get_neighbors():
                        routes.append(new_route)
                routes.remove(route)

        if not len(valid_routes):
            raise MapError("No available routes from start_hub to end_hub")

        # Maps shortest distance from each zone to end and add zones to set
        valid_nodes: set[Zone] = set()

        for route in valid_routes:
            distance_from_end: int = 0
            for node in route:
                if node.distance > distance_from_end or node.distance <= -1:
                    node.distance = distance_from_end
                    valid_nodes.add(node)
                distance_from_end += 1

        # Add 1 to distance point for each restricted zone
        for zone in self.zones.values():
            zone.distance += bool(zone.rule is ZoneRules.RESTRICTED)
            zone.valid_zones = valid_nodes

        ## DEBUG
        # for i in valid_routes:
        #     print()
        #     for j in i:
        #         print(f"{j.__str__()} distance: {j.distance}")

    def process(self) -> None:
        self.init_drones(self.nb_drones)
        self.map_distances()
        while not self.is_finished:
            # Process every drones move one by one
            for drone in self.drones.values():
                drone.current_state.on_event()
            self.logs.end_turn()

            ## TODO REMOVE LATER
            if self.logs.debug:
                print(self.logs.turns_debug[-1])
            print(self.logs.turns[-1], end="\n\n")

            # Check if all drones are done at the end of each turn
            self.is_finished = all([i.current_state is i.states["finished"]
                                    for i in self.drones.values()])
