from src.utils import State
from src.zone import Zone
from enum import Enum


class DroneActions(Enum):
    NONE = 0,
    ADVANCE = 1,


class Drone:
    def __init__(self, id: int, start_zone: Zone) -> None:
        self._id: int = id
        self.current_zone: Zone = start_zone
        self.current_state: State = self.StateNormal(self)
        # self.current_state.on_enter()

    class StateNormal(State):
        def __init__(self, parent: Drone) -> None:
            self.parent: Drone = parent

        def on_enter(self) -> None:
            ...

        def on_event(self, event: int) -> None:
            match event:
                case DroneActions.ADVANCE:
                    next_zones: list[Zone] = \
                            sorted(self.parent.current_zone.get_neighbors(),
                                   key=lambda x: x.distance)
                    for zone in next_zones:
                        ...
                case _:
                    ...
