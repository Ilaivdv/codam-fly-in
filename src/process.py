from src.map import Map


class Process:
    def __init__(self, map: Map) -> None:
        self.map: Map = map

    def process(self) -> None:
        self.map.init_drones(self.map.nb_drones)
        self.map.map_distances()
        while not self.map.is_finished:
            self.map.process_turn()
