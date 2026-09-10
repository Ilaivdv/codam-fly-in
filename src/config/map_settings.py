from pydantic import BaseModel, PrivateAttr
from colorama import Back, Fore, Style
from src import Map, Zone, ZoneType, ZoneRule
import termios
import tty
import sys
import os
import re


class MapError(Exception):
    """ Map error for verbosity """
    pass


class MapValidator(BaseModel):
    _map: Map = Map()

    def raise_map_error(self, msg: str, line_count: int = 0) -> None:
        raise MapError(f"\n{Fore.RED}Error" + (f" at line {line_count}" if
                                               line_count else '') +
                       f"{Fore.RESET}: {msg}")

    def validate_map(self, path: str) -> Map:
        valid_zones: list[str] = [i.value for i in ZoneType]
        valid_metadata: list[str] = ["color", "zone", "max_drones"]

        if not os.path.exists(path):
            self.raise_map_error(f"{path} is not a valid map path")
        elif not os.access(path, os.R_OK):
            self.raise_map_error(f"no permission to read file at path {path}")

        def validate_connection(connection: str, names: list[str],
                                line_count: int) -> bool:
            match = re.fullmatch((r"^connection\s*:\s+"
                                  rf"(?P<n1>\b({'|'.join(names)})\b)-"
                                  rf"(?P<n2>\b({'|'.join(names)})\b)"
                                  rf"(?P<metadata>\s+\[\s*max_link_capacity"
                                  r"=\d+\s*\])*$"),
                                 connection)
            if not match:
                return False
            else:  # Check for duplicate connections before appending
                if not self._map.zones.get(match.group("n1"))\
                        or not self._map.zones.get(match.group("n2")):
                    self.raise_map_error("found undefined connection(s)",
                                         line_count)

                elif self._map.zones[match.group("n1")]\
                        in [i[0] for i in self._map.zones[
                            match.group("n2")].connections]\
                        or match.group("n1") == match.group("n2"):
                    self.raise_map_error("found duplicate connection",
                                         line_count)
                try:
                    self._map.zones[match.group("n1")].connections.append(
                            (self._map.zones[match.group("n2")],
                             (int(match.group("metadata").split(
                                '=', 1)[1].removesuffix(']')) if
                             match.group("metadata") else -1)))
                except ValueError as e:
                    self.raise_map_error(e.__str__(), line_count)
            return True

        def validate_metadata(metadata: list[str], current_zone: str,
                              line_count: int) -> None:
            zone_rules: list[str] = [i.value for i in ZoneRule]
            check_duplicate: list[str] = []

            for i in metadata:
                key, value = i.replace(' ', '').split('=', 1)
                if key not in valid_metadata:
                    self.raise_map_error("found invalid metadata", line_count)
                elif key in check_duplicate:
                    self.raise_map_error("found duplicate metadata value",
                                         line_count)
                match key:
                    case "color":
                        ...  # TODO Find a way to cleanly implement colors
                    case "max_drones":
                        self._map.zones[current_zone].max_drones = int(value)
                    case "zone":
                        ...
                    case _:
                        self.raise_map_error("invalid metadata", line_count)
                check_duplicate.append(key)

        with open(path) as f:
            lines = f.readlines()
            zone_names: list[str] = []
            # Remove all blank/commented lines
            zones: list[tuple[str, int]] = (
                    [(i.strip(), lines.index(i) + 1) for i in lines if
                     not i.startswith('#') and i.strip() != ''])
            if not len(zones):
                self.raise_map_error("file does not contain a map")

            # Check if first option is nb_drones
            if not re.fullmatch(r"^nb_drones\s*:\s+\d+$", zones[0][0]):
                self.raise_map_error("key 'nb_drones' is missing or incorrect",
                                     zones[0][1])
            else:
                self._map.nb_drones = int(zones.pop(0)[0].split(':', 1)[1])

            # Parse through zone configuration with strict regex pattern
            for line, line_count in zones:
                curr_key = re.fullmatch(
                        (rf"^(?P<zone>{'|'.join(valid_zones)})\s*:\s+"
                         r"(?P<name>\b[^\W-]+\b)\s+"
                         r"(?P<coords>-?\d+\s+-?\d+)\s+"
                         rf"(?P<metadata>\[\s*({'|'.join(
                             valid_metadata)})=.+\s*\])*$"),
                        line)
                if not curr_key:
                    # If not zone, check for connection
                    if validate_connection(line, zone_names, line_count):
                        continue
                    self.raise_map_error("incorrect formatting", line_count)
                elif curr_key.group("name") in zone_names:
                    self.raise_map_error("found duplicate name", line_count)
                else:
                    coords: list[str] = curr_key.group("coords").split(' ', 1)
                    curr_zone: Zone = Zone(curr_key.group("zone"),
                                           tuple(map(int, coords)))
                    zone_names.append(curr_key.group("name"))
                    self._map.zones[curr_key.group("name")] = curr_zone
                    if not curr_key.group("metadata"):
                        continue
                    validate_metadata(
                            curr_key.group("metadata")[1:-1].strip().split(
                                ' ', 1),
                            curr_key.group("name"), line_count)
        return self._map


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

    def option_select(self, path: str) -> Map | None:
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
                    return None
                case '\r' | "right":
                    # If it's a file, return the validated map
                    if self._map_options[selected].endswith(".txt"):
                        return self._map_validator.validate_map(
                                    self._map_options[selected])
                    else:
                        for f in os.listdir(self._map_options[selected]):
                            if f.endswith(".txt"):
                                return self.option_select(
                                        self._map_options[selected])
                case "left":
                    # Go back a directory
                    return self.option_select(self._map_options[0].rsplit(
                        '/', 2)[0])
                case "down":
                    if selected < len(self._map_options) - 1:
                        selected += 1
                case "up":
                    if selected > 0:
                        selected -= 1
                case _:
                    pass
