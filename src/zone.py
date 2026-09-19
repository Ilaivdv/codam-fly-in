from colorama import Fore
from enum import StrEnum


class ZoneError(Exception):
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


class Connection:
    def __init__(self, capacity: int, to_zone: Zone) -> None:
        self.capacity: int = capacity
        self.to: Zone = to_zone


class Zone:
    def __init__(self, name: str, type: str, pos: tuple[int, ...]) -> None:
        self.name: str = name
        self.max_drones: int = 1
        self.drone_amount: int = 0
        self.color: str = "gray"

        self.connections: list[Connection] = []
        self.distance: int = -1

        self.type: ZoneTypes = ZoneTypes(type)
        self.rule: ZoneRules = ZoneRules.NORMAL
        self.pos: tuple[int, ...] = pos

    def __str__(self) -> str:
        return self.name

    def get_neighbors(self) -> list[Zone]:
        return [zone.to for zone in self.connections if zone.to is not self]

    def drone_entered(self) -> None:
        self.drone_amount += 1
        if self.drone_amount > self.max_drones:
            raise ZoneError(f"'{self.__str__()}' exceeded max capacity")
