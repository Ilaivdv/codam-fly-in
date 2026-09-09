from pydantic import BaseModel, PrivateAttr
from colorama import Back, Fore, Style
from collections import defaultdict
from typing import Any
import termios
import tty
import sys
import os
import re


class MapError(Exception):
    """ Map error for verbosity """
    pass


class MapValidator(BaseModel):
    _map: dict[str, dict[str, Any] | int] = {}
    _connections: dict[str, list[str]] = defaultdict(list)

    def raise_map_error(self, msg: str, line_count: int = 0) -> None:
        raise MapError(f"\n{Fore.RED}Error" + (f" at line {line_count}" if
                                               line_count else '') +
                       f"{Fore.RESET}: {msg}")

    def validate_map(self, path: str) -> None:
        valid_zones: set[str] = {
                "start_hub",
                "hub",
                "end_hub",
                "connection"
                }
        valid_metadata: set[str] = {
                "color",
                "zone",
                "max_drones",
                "max_link_capacity"
                }

        if not os.path.exists(path):
            self.raise_map_error(f"{path} is not a valid map path")
        elif not os.access(path, os.R_OK):
            self.raise_map_error(f"no permission to read file at path {path}")

        def validate_connection(connection: str, names: list[str]) -> bool:
            match = re.fullmatch((r"^connection\s*:\s+"
                                  rf"(?P<n1>\b({'|'.join(names)})\b)-"
                                  rf"(?P<n2>\b({'|'.join(names)})\b)$"),
                                 connection)
            if not match:
                return False
            else:
                if match.group("n1") in self._connections[match.group("n2")]\
                        or match.group("n1") == match.group("n2"):
                    self.raise_map_error("found duplicate connection")
                self._connections[match.group("n1")].append(match.group("n2"))
            return True

        with open(path) as f:
            lines = f.readlines()
            zone_names: list[str] = []
            # Remove all blank/commented lines
            zones: list[tuple[str, int]] = (
                    [(i.strip(), lines.index(i) + 1) for i in lines if
                     not i.startswith('#') and i.strip() != ''])

            # Check if first option is nb_drones
            if not re.fullmatch(r"^nb_drones\s*:\s+\d+$", zones[0][0]):
                self.raise_map_error("key 'nb_drones' is missing or incorrect",
                                     zones[0][1])
            else:
                self._map["nb_drones"] = int(zones.pop(0)[0].split(':', 1)[1])

            # Parse through zone configuration
            for line, line_count in zones:
                curr_key = re.fullmatch(
                        (rf"^(?P<zone>{'|'.join(valid_zones)})\s*:\s+"
                         r"(?P<name>\b[^\W-]+\b)\s+"
                         r"(?P<coords>-?\d+\s+-?\d+)\s+"
                         rf"(?P<metadata>\[({'|'.join(
                             valid_metadata)})=.+\])*$"),
                        line)
                if not curr_key:
                    # If not zone, check for connection
                    if validate_connection(line, zone_names):
                        continue
                    self.raise_map_error("incorrect formatting", line_count)
                elif curr_key.group("name") in zone_names:
                    self.raise_map_error("found duplicate name", line_count)
                else:
                    zone_names.append(curr_key.group("name"))


class MapSelector(BaseModel):
    _map_options: list[str] = PrivateAttr()
    _map_validator: MapValidator = MapValidator()

    def _get_options(self, path: str) -> None:
        path += '/' if not path.endswith('/') else ''
        res: list[str] = []

        if not os.path.isdir(path) and not os.path.exists(path):
            self._map_validator.raise_map_error(
                    f"{path} is not a valid map directory")
        for i in os.listdir(path):
            i = path + i
            if not os.path.isdir(i) and not os.path.isfile(i):
                self._map_validator.raise_map_error(
                        f"{path} is not a valid map directory/file")
            if i.endswith(".txt"):
                res.append(i)
            elif os.path.isdir(i):
                res.append(i + '/')
        self._map_options = res

    def option_select(self, path: str) -> None:
        self._get_options(path)

        def read_key() -> str:
            original_settings = termios.tcgetattr(sys.stdin)
            try:
                _ = tty.setraw(sys.stdin.fileno())
                key: str = sys.stdin.read(1)
                if key == '\x1b':  # Escape sequence start
                    # Read next two bytes to get escape sequence
                    key += sys.stdin.read(2)
                    key_map = {
                        '\x1b[A': 'up',
                        '\x1b[B': 'down',
                        '\x1b[C': 'right',
                        '\x1b[D': 'left'
                    }
                    return key_map.get(key, 'unknown')
                return key
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN,
                                  original_settings)

        selected: int = 0
        while True:
            print("\033c -- Press Q to quit\n")
            for i, option in enumerate(self._map_options):
                if i == selected:
                    print(Back.WHITE, Fore.BLACK, option, Style.RESET_ALL,
                          sep='')
                    continue
                print(option)

            match read_key():
                case 'q':
                    print("\033c")
                    return
                case '\r' | "right":
                    if self._map_options[selected].endswith(".txt"):
                        self._map_validator.validate_map(
                                self._map_options[selected])
                    else:
                        self.option_select(self._map_options[selected])
                    return
                case "left":
                    self.option_select(self._map_options[0].rsplit('/', 2)[0])
                    return
                case "down":
                    if selected < len(self._map_options) - 1:
                        selected += 1
                case "up":
                    if selected > 0:
                        selected -= 1
                case _:
                    pass
