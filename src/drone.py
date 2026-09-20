from src.zone import Zone, ZoneRules, ZoneTypes, Node
from src.utils import State, Logs


class Drone:
    def __init__(self, id: int, start_zone: Zone, log: Logs) -> None:
        self._id: int = id
        self.current_node: Node = start_zone

        self.logs: Logs = log
        self.states: dict[str, State] = {
                "normal": self.StateNormal(self),
                "waiting": self.StateWaiting(self),
                "finished": self.StateFinished(self),
                }
        self.current_state: State = self.states["normal"]

    def _move_to_zone(self, to_zone: Zone) -> None:
        self.current_node.drone_exited()
        self.current_node = to_zone
        self.current_node.drone_entered()

        if to_zone.rule is ZoneRules.RESTRICTED:
            self.logs.log_drone_action(f"D{self._id}-connection-{to_zone}")
            self.next_state(self.states["waiting"])
        else:
            self.logs.log_drone_action(f"D{self._id}-{to_zone}")
        if to_zone.type is ZoneTypes.END:
            self.next_state(self.states["finished"])

    def next_state(self, to_state: State) -> None:
        self.current_state = to_state
        self.current_state.on_enter()

    # Drone states
    class StateNormal(State):
        def __init__(self, parent: Drone) -> None:
            self.parent: Drone = parent

        def on_enter(self) -> None:
            self.parent.logs.log_debug((f"D{self.parent._id} entered state "
                                        f"{self.__str__()}"))

        def on_event(self) -> None:
            zones: list[Zone] = \
                    sorted(self.parent.current_node.get_valid_neighbors(),
                           key=lambda x: x.distance)
            next_zone: Node | None = None
            for zone in zones:
                if not next_zone:
                    next_zone = zone
                if next_zone.drone_amount == next_zone.max_drones:
                    next_zone = None
                    continue
                ## TODO Add check for connection capacity in a turn
                match zone.rule:
                    case ZoneRules.BLOCKED:
                        if zone is next_zone:
                            next_zone = None
                    case ZoneRules.PRIORITY:
                        next_zone = zone
                        break
                    case _:
                        pass
            if not next_zone:
                self.parent.next_state(self.parent.states["waiting"])
            else:
                self.parent._move_to_zone(next_zone)

    class StateWaiting(State):
        def __init__(self, parent: Drone) -> None:
            self.parent: Drone = parent

        def on_enter(self) -> None:
            self.parent.logs.log_debug((f"D{self.parent._id} entered state "
                                        f"{self.__str__()}"))

        def on_event(self) -> None:
            ## TODO Add check for end_hub to finished state
            self.parent.next_state(self.parent.states["normal"])
            self.parent.current_state.on_event()

    class StateFinished(State):
        def __init__(self, parent: Drone) -> None:
            self.parent: Drone = parent

        def on_enter(self) -> None:
            self.parent.logs.log_debug(f"D{self.parent._id} is finished")

        def on_event(self) -> None:
            pass
