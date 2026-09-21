from src.render.map_select import MapProcess
from src.utils import Logs
from src.map import Map

class PygameRenderer(MapProcess):
    def __init__(self, logs: Logs) -> None:
        super().__init__(logs)

    def map_select(self, files: list[str]) -> Map:
        ...

    def process_turn(self) -> None:
        ...

    def on_input(self) -> bool:
        ...
