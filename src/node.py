from abc import ABC, abstractmethod
from colorama import Fore
from enum import StrEnum


class NodeError(Exception):
    """ Zone error for verbosity """

    def __init__(self, msg: str) -> None:
        """ Initializes error with colored formatting. """

        super().__init__(f"\n{Fore.RED}Zone error{Fore.RESET}: {msg}")


class ZoneTypes(StrEnum):
    """ Enum storing all valid Zone types. """

    START = "start_hub"
    HUB = "hub"
    END = "end_hub"


class ZoneRules(StrEnum):
    """ Enum storing all valid Zone restrictions. """

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Node(ABC):
    """
    Abstract Node class with methods for keeping track of Drones and
    neighboring Nodes.
    """

    def __init__(self, parent: Zone | Connection, name: str,
                 max_drones: int = 1, distance: int = -1) -> None:
        """
        Initializes a Node.

        Args:
            parent: Either a Zone or Connection definings Node's parent.
            name: Node's name.
            max_drones: Node's maximum capacity of Drones.
            distance: Distance from final Node.
        """

        self.parent: Zone | Connection = parent
        self.name: str = name
        self.distance: int = distance

        self.max_drones: int = max_drones
        self.drone_amount: int = 0

    def __str__(self) -> str:
        """ Returns Node's name. """

        return self.name

    @abstractmethod
    def get_neighbors(self) -> list[Node]:
        """ Return list of neighboring Nodes. """
        ...

    @abstractmethod
    def get_valid_neighbors(self) -> list[Node]:
        """
        Return list of valid neighboring Nodes.
        (valid being a Node that has a path to the end)
        """
        ...

    @abstractmethod
    def get_current_zone(self) -> Zone:
        """ Returns current Zone inheriting from Node. """
        ...

    def drone_entered(self) -> None:
        """
        Adds 1 to how many Drones Node is holding.

        Raises:
            NodeError: If Node's capacity exceeds max_drones.
        """

        self.drone_amount += 1
        if self.drone_amount > self.max_drones:
            raise NodeError((f"'{self.__str__()}' exceeded max capacity of "
                             f"{self.max_drones}"))

    def drone_exited(self) -> None:
        """
        Removes 1 from how many Drones Node is holding.

        Raises:
            NodeError: If more Drones leave than Node is currently holding.
        """

        self.drone_amount -= 1
        if self.drone_amount < 0:
            raise NodeError(f"'{self.__str__()}' is holding negative drones")


class Connection(Node):
    """ Node that connects Zones to each other. """

    def __init__(self, max_drones: int, to_zone: Zone,
                 behind: bool = False) -> None:
        """
        Initializes Connection to Zone.

        Args:
            max_drones: Maximum number of drones that this Connection can hold.
            to_zone: Zone that Connection is connecting to.
            behind: If Connection is connecting to a Zone behind current Zone.
        """

        self.to: Zone = to_zone
        self.is_behind: bool = behind
        super().__init__(
                parent=self,
                name=f"connection-{to_zone.__str__()}",
                max_drones=max_drones,
                distance=self.to.distance)

    def __str__(self) -> str:
        return super().__str__()

    def get_neighbors(self) -> list[Node]:
        return [self.to]

    def get_valid_neighbors(self) -> list[Node]:
        return [self.to]

    def get_current_zone(self) -> Zone:
        """ Returns Zone that Connection is connecting to. """
        return self.to


class Zone(Node):
    def __init__(self, name: str, type: str, pos: tuple[int, int]) -> None:
        """
        Initializes a Zone.
        Attributes like rule and color have defaults but get overwritten
        during map parsing if new value is found.

        Connections get Initialized and set later during parsing as well.

        Args:
            name: Zone's name.
            type: A validated zone type from Enum ZoneTypes.
            pos: X, Y position of Zone.
        """

        self.color: str = "gray"

        self.connections: list[Connection] = []
        self.valid_zones: set[Zone]

        self.type: ZoneTypes = ZoneTypes(type)
        self.rule: ZoneRules = ZoneRules.NORMAL
        self.pos: tuple[int, int] = pos
        super().__init__(self, name)

    def __str__(self) -> str:
        return super().__str__()

    def get_neighbors(self) -> list[Node]:
        return [node for node in self.connections if node.to is not self]

    def get_valid_neighbors(self) -> list[Node]:
        return [node for node in self.connections if node.to is not self
                and node.to in self.valid_zones]

    def get_current_zone(self) -> Zone:
        return self
