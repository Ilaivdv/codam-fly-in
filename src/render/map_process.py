from src.parsing import MapValidator, ParseError
from abc import ABC, abstractmethod
from src.utils import Logs
from src.map import Map
from time import sleep
import os


class MapProcess(ABC):
    """
    Abstract class holding required methods for setting up the simulation
    and storing data needed for rendering.
    """

    def __init__(self, logs: Logs, auto_advance: bool = True) -> None:
        """
        Initializes MapProcess and prepares for Map selection.

        Args:
            logs: Logger to pass around to objects in the simulation.
            auto_advance: Automatically advance turns until end is reached.
                If False, listens for input after every turn to keep going.
        """

        self._map_validator: MapValidator = MapValidator(logs)
        self._auto_advance_turns: bool = auto_advance
        self._logs: Logs = logs
        self._map: Map

    def get_options(self, path: str) -> list[str]:
        """
        Gets all directories and .txt files.

        Args:
            path: The path to read from.

        Raises:
            ParseError: If path/file is invalid in any any.

        Returns:
            list[str]: List containing all directories and .txt files at given
                path.
        """

        path += '/' if not path.endswith('/') else ''
        res: list[str] = []

        if not os.path.isdir(path) and not os.path.exists(path):
            raise ParseError(f"{path} is not a valid map directory")
        for i in os.listdir(path):
            i = path + i
            if not os.path.isdir(i) and not os.path.isfile(i):
                raise ParseError(f"{path} is not a valid map directory/file")
            if i.endswith(".txt"):
                res.append(i)
            elif os.path.isdir(i):
                res.append(i + '/')
        return res

    def start_process(self, map_path: str, turn_delay: float = 0.0) -> None:
        """
        Goes through map select on given path to get Map,
        starts the simulation, going through turns either automatically or one
        by one.

        Args:
            map_path: Path to look for maps in.
            turn_delay: The delay in ms between each turn
                (only for auto_advance)
        """

        self._map = self.map_select(self.get_options(map_path))
        print("\033c")

        while not self._map.is_finished:
            self.process_turn(self._auto_advance_turns)
            if self._auto_advance_turns:
                sleep(turn_delay)
        self.on_process_finished()

    @abstractmethod
    def map_select(self, files: list[str]) -> Map:
        """
        Abstract method for map selection and validation.

        Args:
            files: Options to show in selection.

        Returns:
            Map: Selected .txt file as a validated Map.
        """
        ...

    @abstractmethod
    def process_turn(self, auto_advance: bool) -> None:
        """
        Processes 1 turn of the simulation, listens for input when
        auto_advance is False.
        """
        ...

    @abstractmethod
    def on_process_finished(self) -> None:
        """ Method that gets called after process is finished. """
        ...
