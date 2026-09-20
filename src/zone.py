from abc import ABC, abstractmethod
from colorama import Fore
from enum import StrEnum


class NodeError(Exception):
    """ Zone error for verbosity """

    def __init__(self, msg: str, line: int = 0) -> None:
        super().__init__(f"\n{Fore.RED}Zone error{Fore.RESET}: {msg}")


class ZoneTypes(StrEnum):
    START = "start_hub"
    HUB = "hub"
    END = "end_hub"


class ZoneRules(StrEnum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Node(ABC):
    def __init__(self, parent: Zone | Connection, name: str,
                 max_drones: int = 1, distance: int = -1) -> None:
        self.parent: Zone | Connection = parent
        self.name: str = name
        self.distance: int = distance

        self.max_drones: int = max_drones
        self.drone_amount: int = 0

    def __str__(self) -> str:
        return self.name

    @abstractmethod
    def get_neighbors(self) -> list[Node]:
        ...

    @abstractmethod
    def get_valid_neighbors(self) -> list[Node]:
        ...

    @abstractmethod
    def get_current_zone(self) -> Zone:
        ...

    def drone_entered(self) -> None:
        self.drone_amount += 1
        if self.drone_amount > self.max_drones:
            raise NodeError((f"'{self.__str__()}' exceeded max capacity of "
                             f"{self.max_drones}"))

    def drone_exited(self) -> None:
        self.drone_amount -= 1
        if self.drone_amount < 0:
            raise NodeError(f"'{self.__str__()}' is holding negative drones")


class Connection(Node):
    def __init__(self, max_drones: int, to_zone: Zone,
                 behind: bool = False) -> None:
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
        return self.to


class Zone(Node):
    def __init__(self, name: str, type: str, pos: tuple[int, ...]) -> None:
        self.color: str = "gray"

        self.connections: list[Connection] = []
        self.valid_zones: set[Zone]

        self.type: ZoneTypes = ZoneTypes(type)
        self.rule: ZoneRules = ZoneRules.NORMAL
        self.pos: tuple[int, ...] = pos
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
