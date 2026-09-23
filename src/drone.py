from src.node import Zone, ZoneRules, ZoneTypes, Connection, Node
from src.utils import State, Logs


class Drone:
    """
    A Drone class holding methods for efficiently navigating pre-mapped routes.
    """

    def __init__(self, id: int, start_zone: Zone, log: Logs) -> None:
        """
        Initializes drone.

        Args:
            id: Unique integer value representing Drone's id.
            start_zone: Starting point for Drone.
            log: Logger which Drone will log its movements to.
        """

        self._id: int = id
        self.current_node: Node = start_zone
        self.last_connection: Connection | None = None
        self._queued_zone: Zone | None = None

        self.logs: Logs = log
        self.states: dict[str, State] = {
                "normal": self.StateNormal(self),
                "waiting": self.StateWaiting(self),
                "finished": self.StateFinished(self),
                }
        self.current_state: State = self.states["normal"]

    def _move_to_node(self, to_node: Node,
                      skip_connection: bool = True) -> None:
        """
        Moves to a given node and calls enter and exit methods for that node
        to update its capacity.

        On final Zone entered, Drone will change state to finished,
        waiting until the end of the program.

        Args:
            to_node: Node object to move to, can be either Connection or Zone.
            skip_connection: Whether to skip over Connection and move to
                its connected Zone occupying both nodes for that turn.
        """

        self.current_node.drone_exited()
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
        """ Advances Drone to next state and calls its on_enter() method. """

        self.current_state = to_state
        self.current_state.on_enter()

    def add_to_queue(self, zone: Zone) -> None:
        """
        Adds a Zone to Drone's queue for the next turn.
        Makes Zone's distance cost temporarily more expensive for other Drones.

        Stops early if queue is already occupied.
        """

        if self._queued_zone:
            return
        self._queued_zone = zone
        self._queued_zone.distance += 1

    def pop_from_queue(self) -> None:
        """ Clear Zone from queue and restore Zone's distance cost. """

        if type(self._queued_zone) is Zone:
            self._queued_zone.distance -= 1
        self._queued_zone = None

    # -- DRONE STATES --
    class StateNormal(State):
        """ Drone's normal State, decides best next move to make. """

        def __init__(self, parent: Drone) -> None:
            super().__init__(parent)

        def on_enter(self) -> None:
            """ Logs entered State to Log's debug. """

            self.parent.logs.log_debug(
                    f"D{self.parent._id} is in normal state")

        def on_event(self) -> None:
            """
            Decides most efficient next move to make.

            Sorts neighboring nodes by shortest distance and advances to
            the first one if capacity allows it or, first available Zone
            with rule PRIORITY.

            If no available Zones are found, or if its more beneficial to wait,
            Drone will enter waiting State and wait not make any movements for
            the turn.
            """

            # Valid neighbors are adjacent nodes that have a route to end_hub
            nodes: list[Node] = \
                    sorted(self.parent.current_node.get_valid_neighbors(),
                           key=lambda x: x.distance)
            next_node: Node | None = None

            self.parent.logs.log_debug((f"D{self.parent._id} options: "
                                        f"{[i.__str__() + " " + str(
                                         i.distance) for i in nodes
                                        if type(i) is Connection
                                        and not i.is_behind]}"))

            self.parent.pop_from_queue()

            prev_node: Node | None = None
            for node in nodes:
                if type(node) is Connection and node.is_behind:
                    continue

                # Gets zone even if current node is connection
                zone: Zone = node.get_current_zone()

                # Restricted zones pass because zone will have space after wait
                if node.drone_amount == node.max_drones or \
                        zone.drone_amount == zone.max_drones and \
                        not zone.rule is ZoneRules.RESTRICTED:
                    prev_node = node
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
                    if prev_node and node.distance - prev_node.distance > 2:
                        next_node = prev_node
                        self.parent.add_to_queue(next_node.get_current_zone())
                    else:
                        next_node = node

            if not next_node or self.parent._queued_zone:
                self.parent.next_state(self.parent.states["waiting"])
            else:
                # Sets to False if next zone is restricted
                skip_connection: bool = not next_node.get_current_zone().rule\
                        is ZoneRules.RESTRICTED

                self.parent._move_to_node(next_node, skip_connection)

    class StateWaiting(State):
        def __init__(self, parent: Drone) -> None:
            super().__init__(parent)

        def on_enter(self) -> None:
            """ Logs entered State to Log's debug. """

            self.parent.logs.log_debug(f"D{self.parent._id} is waiting")

        def on_event(self) -> None:
            """
            Switches States to normal to check whether a new Node is
            available to move to.
            """

            self.parent.next_state(self.parent.states["normal"])
            self.parent.current_state.on_event()

    class StateFinished(State):
        def __init__(self, parent: Drone) -> None:
            super().__init__(parent)

        def on_enter(self) -> None:
            """ Logs entered State to Log's debug. """

            self.parent.logs.log_debug(f"D{self.parent._id} is finished")

        def on_event(self) -> None:
            """
            Clears last entered connection if present, otherwise does
            nothing.
            """

            if self.parent.last_connection is not None:
                self.parent.last_connection.drone_exited()
                self.parent.last_connection = None
