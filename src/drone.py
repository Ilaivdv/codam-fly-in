from src.utils import State
from src.zone import Zone, ZoneRules


class Drone:
    def __init__(self, id: int, start_zone: Zone) -> None:
        self._id: int = id
        self.current_zone: Zone = start_zone

        self._states: dict[str, State] = {
                "normal": self.StateNormal(self),
                "restricted": self.StateRestricted(self),
                "waiting": self.StateWaiting(self),
                }
        self.current_state: State = self._states["normal"]

    def advance_to_zone(self, to: Zone) -> None:
        self.current_zone = to
        self.current_zone.drone_amount += 1

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
                elif next_zone.drone_amount == next_zone.max_drones:
                    next_zone = None
                match zone.rule:
                    case ZoneRules.BLOCKED:
                        if next_zone is zone:
                            next_zone = None
                    case ZoneRules.RESTRICTED:
                        self.parent.current_state = \
                                self.parent._states["restricted"]
                        ... # Move to a connection
                    case ZoneRules.PRIORITY:
                        next_zone = zone
                        break
                    case _:
                        pass
            if not next_zone:
                # Enter waiting state
                ...

    class StateRestricted(State):
        def __init__(self, parent: Drone) -> None:
            self.parent: Drone = parent

        def on_enter(self) -> None:
            ...

        def on_event(self) -> None:
            ...

    class StateWaiting(State):
        def __init__(self, parent: Drone) -> None:
            self.parent: Drone = parent

        def on_enter(self) -> None:
            ...

        def on_event(self) -> None:
            ...
