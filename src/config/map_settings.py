from pydantic import BaseModel, PrivateAttr, Field
from colorama import Back, Fore, Style
from typing import Any
import termios
import tty
import sys
import os


class MapError(Exception):
    """ Map error for verbosity """
    pass


class MapValidator(BaseModel):
    _keys: set[str] = PrivateAttr({
        "start_hub",
        "end_hub",
        "hub",
        "connection",
       })
    _map: dict[str, int | dict[str, Any]] = {}

    def validate_map(self, path: str) -> None:
        nb_drones: int = Field(gt=0)

        with open(path) as f:
            lines: list[str] = f.readlines()
            has_nb: bool = False

            for line_count, line in enumerate(lines):
                if line.startswith('#') or not len(line.strip()):
                    continue
                elif line.startswith("nb_drones"):
                    nb_drones = int(line.split(':', 1)[1].strip())
                    self._map["nb_drones"] = nb_drones
                    has_nb = True
                    continue
                elif not has_nb:
                    raise MapError((f"at line {line_count}: file must start"
                                    "with key 'nb_drones' with a positive "
                                    "integer value"))
                if line.split(':')[0] in self._keys:
                    key: str = line.split(':')[0].strip()
                    match key:
                        case key if key == "start_hub" or key == "end_hub":
                            if self._map.get(key) != None:
                                raise MapError((f"at line {line_count}: "
                                                f"duplicate key '{key}'"))
                            self._map[key] = 0
                        case _:
                            pass
                else:
                    raise MapError((f"at line {line_count}: invalid key "
                                    f"'{line.split(':')[0]}'"))


class MapSelector(BaseModel):
    _map_options: list[str] = PrivateAttr()
    _map_validator: MapValidator = MapValidator()

    def _get_options(self, path: str) -> None:
        path += '/' if not path.endswith('/') else ''
        res: list[str] = []

        if not os.path.isdir(path) and not os.path.lexists(path):
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
                    # Map sequences to key names
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
