from src.node import Zone, Connection, ZoneTypes, ZoneRules
from src.utils import Logs
from colorama import Fore
from src.map import Map
import sys
import os
import re


class ParseError(Exception):
    """ Parse error for verbosity """

    def __init__(self, msg: str, line: int = 0) -> None:
        super().__init__(f"\n{Fore.RED}ParseError" +
                         (f" at line {line}" if line else '') +
                         f"{Fore.RESET}: {msg}")


class MapValidator:
    def __init__(self, logs: Logs) -> None:
        self._map: Map = Map(logs)
        self._logs: Logs = logs

    def validate_map(self, path: str) -> Map:
        valid_zones: list[str] = [i.value for i in ZoneTypes]
        valid_metadata: list[str] = ["color", "zone", "max_drones"]

        # Checks if path is readable and exists
        if not os.path.exists(path):
            raise ParseError(f"{path} is not a valid map path")
        elif not os.access(path, os.R_OK):
            raise ParseError(f"no permission to read file at path {path}")

        def validate_connection(connection: str, names: list[str],
                                line_count: int) -> bool:
            match = re.fullmatch((r"^connection\s*:\s+"
                                  rf"(?P<n1>\b({'|'.join(names)})\b)-"
                                  rf"(?P<n2>\b({'|'.join(names)})\b)"
                                  rf"(?P<metadata>\s+\[\s*max_link_capacity"
                                  r"=\d+\s*\])?$"),
                                 connection)
            if not match:
                return False
            else:  # Check for duplicate connections before appending
                if not self._map.zones.get(match.group("n1")) \
                        or not self._map.zones.get(match.group("n2")):
                    raise ParseError("found undefined connection(s)",
                                     line_count)

                elif self._map.zones[match.group("n2")] in \
                        [i.get_current_zone() for i
                         in self._map.zones[match.group(
                            "n1")].get_neighbors()] \
                        or match.group("n1") == match.group("n2"):
                    raise ParseError("found duplicate connection", line_count)
                try:
                    max_capacity: int = (int(match.group("metadata").split(
                                '=', 1)[1].removesuffix(']'))
                                         if match.group("metadata") else 1)

                    self._map.zones[match.group("n1")].connections.append(
                            Connection(max_drones=max_capacity,
                                       to_zone=self._map.zones[
                                           match.group("n2")]))
                    self._map.zones[match.group("n2")].connections.append(
                            Connection(max_drones=max_capacity,
                                       to_zone=self._map.zones[
                                           match.group("n1")],
                                       behind=True))

                except ValueError as e:
                    raise ParseError(e.__str__(), line_count)
            return True

        def validate_metadata(metadata: list[str], current_zone: str,
                              line_count: int) -> None:
            check_duplicate: list[str] = []

            for i in metadata:
                # Clean up and split metadata keys and values
                key, value = i.replace(' ', '').split('=', 1)
                if key not in valid_metadata:
                    raise ParseError("found invalid metadata key", line_count)

                # Every saved key gets added to a list to check for duplicates
                elif key in check_duplicate:
                    raise ParseError("found duplicate metadata value",
                                     line_count)
                match key:
                    case "color":
                        self._map.zones[current_zone].color = value
                    case "max_drones":
                        try:
                            max_drones: int = int(value)
                            if max_drones < 0:
                                raise ParseError("invalid value in max_drones",
                                                 line_count)
                            if self._map.zones[current_zone].type is\
                                    ZoneTypes.START or\
                                    self._map.zones[current_zone].type is\
                                    ZoneTypes.END:
                                ...  ## TODO Add warning log here later
                            self._map.zones[
                                    current_zone].max_drones = int(value)
                        except ValueError as e:
                            raise ParseError(e.__str__(), line_count)
                    case "zone":
                        try:
                            self._map.zones[current_zone].rule = ZoneRules(
                                    value)
                        except ValueError as e:
                            raise ParseError(e.__str__(), line_count)
                    case _:
                        raise ParseError("invalid key in metadata", line_count)
                check_duplicate.append(key)

        with open(path) as f:
            lines = f.readlines()
            zone_names: list[str] = []

            # Remove all blank/commented lines
            zones: list[tuple[str, int]] = (
                    [(i.strip(), lines.index(i) + 1) for i in lines if
                     not i.startswith('#') and i.strip() != ''])
            if not len(zones):
                raise ParseError("file does not contain a map")

            # Check if first option is nb_drones
            if not re.fullmatch(r"^nb_drones\s*:\s+\d+$", zones[0][0]):
                raise ParseError("key 'nb_drones' is missing or incorrect",
                                 zones[0][1])
            else:
                nb_drones: int = int(zones.pop(0)[0].split(':', 1)[1])
                if nb_drones < 1:
                    raise ParseError("program can't run with 0 drones",
                                     zones[0][1])
                elif nb_drones > sys.maxsize:
                    raise ParseError("nb_drones exceeds systems max size",
                                     zones[0][1])

                # Initialize nb_drones
                self._map.nb_drones = nb_drones

            # Parse through zone configuration with strict regex pattern
            for line, line_count in zones:
                curr_key = re.fullmatch(
                        (rf"^(?P<zone>{'|'.join(valid_zones)})\s*:\s+"
                         r"(?P<name>\b[^\W-]+\b)\s+"
                         r"(?P<coords>-?\d+\s+-?\d+)\s+"
                         rf"(?P<metadata>\[\s*({'|'.join(
                             valid_metadata)})=.+\s*\])?$"),
                        line)
                if not curr_key:

                    # If zone not found in key, check for connection
                    if validate_connection(line, zone_names, line_count):
                        continue
                    raise ParseError("incorrect formatting", line_count)
                elif curr_key.group("name") in zone_names:
                    raise ParseError("found duplicate name", line_count)
                else:

                    # Initialize new zone and validate metadata
                    coords: list[str] = curr_key.group("coords").split(' ', 1)
                    curr_zone: Zone = Zone(name=curr_key.group("name"),
                                           type=curr_key.group("zone"),
                                           pos=(int(coords[0]), int(coords[1])
                                                ))
                    self._map.zones[curr_zone.name] = curr_zone
                    zone_names.append(curr_zone.name)

                    if curr_key.group("metadata"):
                        validate_metadata(
                                curr_key.group("metadata")[1:-1].strip().split(
                                    ' '),
                                curr_key.group("name"), line_count)

        self._map.validate_positions()  # Raises error on overlap
        self._map.init_level()  # Raises pathfinding errors if there are any
        return self._map
