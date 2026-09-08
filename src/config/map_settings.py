from pydantic import BaseModel, PrivateAttr
from colorama import Back, Fore, Style
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
    _map: dict[str, int | dict[str, Any]] = {}

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

        with open(path) as f:
            lines = f.readlines()
            zone_names: list[str] = []
            zones: list[tuple[str, int]] = (
                    [(i.strip(), lines.index(i) + 1) for i in lines if
                     not i.startswith('#') and i.strip() != ''])

            if not re.fullmatch(r"^nb_drones\s*:\s*\d+$", zones[0][0]):
                self.raise_map_error("key 'nb_drones' is missing or incorrect",
                                     zones[0][1])
            else:
                self._map["nb_drones"] = int(zones.pop(0)[0].split(':', 1)[1])
            for line, line_count in zones:
                curr_key = re.match(
                        (rf"^(?P<zone>{'|'.join(valid_zones)})\s*:\s*"
                         r"(?P<name>\b[^\W-]+\b)\s*"
                         r"(?P<coords>-?\d+\s*-?\d+)\s*"),
                        line)
                if not curr_key:
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
            raise MapError(f"{path} is not a valid map directory")
        for i in os.listdir(path):
            i = path + i
            if not os.path.isdir(i) and not os.path.isfile(i):
                raise MapError(f"{i} is not a valid map directory/file")
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
                    print(Back.WHITE, Fore.BLACK, option, Style.RESET_ALL)
                    continue
                print(option)

            key_pressed = read_key()
            if key_pressed == 'q':
                print("\033c")
                return
            elif key_pressed == '\r' or key_pressed == "right":
                if self._map_options[selected].endswith(".txt"):
                    self._map_validator.validate_map(
                            self._map_options[selected])
                else:
                    self.option_select(self._map_options[selected])
                return
            elif key_pressed == "left":
                self.option_select(self._map_options[0].rsplit('/', 2)[0])
                return
            elif key_pressed == "down" and \
                    selected < len(self._map_options) - 1:
                selected += 1
            elif key_pressed == "up" and selected > 0:
                selected -= 1
