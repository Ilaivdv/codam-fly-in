from src.utils import State
from src.map import Zone


class Drone:
    def __init__(self, id: int, start_zone: Zone) -> None:
        self._id: int = id

    class StateNormal(State):
        def on_enter(self) -> None:
            pass

        def on_event(self, event: int) -> None:
            ...
