from src.map import Map


class Process:
    def __init__(self, map: Map) -> None:
        self.map: Map = map

    def start_next_turn(self):
        ...
