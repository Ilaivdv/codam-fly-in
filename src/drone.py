from src.node import Zone, ZoneRules, ZoneTypes, Connection, Node
from src.utils import State, Logs


class Drone:
    def __init__(self, id: int, start_zone: Zone, log: Logs) -> None:
        self._id: int = id
        self.current_node: Node = start_zone
        self.last_connection: Connection | None = None
        self.last_node: Node = start_zone

        self.logs: Logs = log
        self.states: dict[str, State] = {
                "normal": self.StateNormal(self),
                "waiting": self.StateWaiting(self),
                "finished": self.StateFinished(self),
                }
        self.current_state: State = self.states["normal"]

    def _move_to_node(self, to_node: Node,
                      skip_connection: bool = True) -> None:
        self.current_node.drone_exited()
        self.last_node = self.current_node
        self.current_node = to_node
        self.current_node.drone_entered()

        if self.last_connection is not None:
            self.last_connection.drone_exited()
            self.last_connection = None

        # When skipping connection, still enter to keep track of its capacity
        if skip_connection and type(to_node.parent) is Connection:
            to_zone: Zone = to_node.get_current_zone()
            self.current_node = to_zone
            self.current_node.drone_entered()
            self.last_connection = to_node.parent

        if type(self.current_node) is Zone and \
                self.current_node.type is ZoneTypes.END:
            self.next_state(self.states["finished"])

        # Add action to current turn
        self.logs.log_drone_action(
                f"D{self._id}-{self.current_node.__str__()}")

    def next_state(self, to_state: State) -> None:
        self.current_state = to_state
        self.current_state.on_enter()

    # Drone states
    class StateNormal(State):
        def __init__(self, parent: Drone) -> None:
            self.parent: Drone = parent

        def on_enter(self) -> None:
            self.parent.logs.log_debug(
                    f"D{self.parent._id} is in normal state")

        def on_event(self) -> None:
            nodes: list[Node] = \
                    sorted(self.parent.current_node.get_valid_neighbors(),
                           key=lambda x: x.distance)
            next_node: Node | None = None

            self.parent.logs.log_debug((f"D{self.parent._id} options: "
                                        f"{[i.__str__() + " " + str(
                                         i.distance) for i in nodes]}"))

            for node in nodes:
                if type(node) is Connection and node.is_behind:
                    continue

                # Gets zone even if current node is connection
                zone: Zone = node.get_current_zone()

                if node.drone_amount == node.max_drones or \
                        zone.drone_amount == zone.max_drones:
                    continue

                match zone.rule:
                    case ZoneRules.BLOCKED:
                        continue
                    case ZoneRules.PRIORITY:
                        next_node = node
                        break
                    case _:
                        pass

                if not next_node:
                    next_node = node

            if not next_node:
                # Wait for the next turn if no option is found
                self.parent.next_state(self.parent.states["waiting"])
            else:
                # Sets to False if next zone is restricted
                skip_connection: bool = not next_node.get_current_zone().rule\
                        is ZoneRules.RESTRICTED

                self.parent._move_to_node(next_node, skip_connection)

    class StateWaiting(State):
        def __init__(self, parent: Drone) -> None:
            self.parent: Drone = parent

        def on_enter(self) -> None:
            self.parent.logs.log_debug(f"D{self.parent._id} is waiting")

        def on_event(self) -> None:
            self.parent.next_state(self.parent.states["normal"])
            self.parent.current_state.on_event()

    class StateFinished(State):
        def __init__(self, parent: Drone) -> None:
            self.parent: Drone = parent

        def on_enter(self) -> None:
            self.parent.logs.log_debug(f"D{self.parent._id} is finished")

        def on_event(self) -> None:
            if self.parent.last_connection is not None:
                self.parent.last_connection.drone_exited()
                self.parent.last_connection = None
