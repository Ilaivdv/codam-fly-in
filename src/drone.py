from src.zone import Zone, ZoneRules, ZoneTypes
from src.utils import State


class Drone:
    def __init__(self, id: int, start_zone: Zone) -> None:
        self._id: int = id
        self.current_zone: Zone = start_zone

        self._states: dict[str, State] = {
                "normal": self.StateNormal(self),
                "waiting": self.StateWaiting(self),
                "finished": self.StateFinished(self),
                }
        self.current_state: State = self._states["normal"]

    def _move_to_zone(self, to_zone: Zone) -> None:
        self.current_zone.drone_exited()
        self.current_zone = to_zone
        self.current_zone.drone_entered()
        if to_zone.rule is ZoneRules.RESTRICTED:
            ## TODO Add log for drone being in connection
            self.current_state = self._states["waiting"]
        elif to_zone.type is ZoneTypes.END:
            self.current_state = self._states["finished"]

        ## DEBUG
        print(f"D{self._id}-{to_zone}")

    # Drone states
    class StateNormal(State):
        def __init__(self, parent: Drone) -> None:
            self.parent: Drone = parent

        def on_enter(self) -> None:
            pass

        def on_event(self) -> None:
            zones: list[Zone] = \
                    sorted(self.parent.current_zone.get_neighbors(),
                           key=lambda x: x.distance)
            next_zone: Zone | None = None
            for zone in zones:
                if not next_zone:
                    next_zone = zone
                if next_zone.drone_amount == next_zone.max_drones:
                    next_zone = None
                    continue
                ## TODO Add check for connection capacity in a turn
                match zone.rule:
                    case ZoneRules.BLOCKED:
                        if next_zone is zone:
                            next_zone = None
                    case ZoneRules.PRIORITY:
                        next_zone = zone
                        break
                    case _:
                        pass
            if not next_zone:
                self.parent.current_state = self.parent._states["waiting"]
            else:
                self.parent._move_to_zone(next_zone)

    class StateWaiting(State):
        def __init__(self, parent: Drone) -> None:
            self.parent: Drone = parent

        def on_enter(self) -> None:
            ...

        def on_event(self) -> None:
            ## TODO Add check for end_hub to finished state
            self.parent.current_state = self.parent._states["normal"]
            self.parent.current_state.on_event()

    class StateFinished(State):
        def __init__(self, parent: Drone) -> None:
            self.parent: Drone = parent

        def on_enter(self) -> None:
            ...

        def on_event(self) -> None:
            ...
