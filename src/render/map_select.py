from src.parsing import MapValidator, ParseError
from abc import ABC, abstractmethod
from src.utils import Logs
from src.map import Map
from time import sleep
from typing import Any
import os


class MapProcess(ABC):
    def __init__(self, logs: Logs) -> None:
        self._map_validator: MapValidator = MapValidator(logs)
        self._auto_advance_turns: bool = True
        self._logs: Logs = logs
        self._map: Map

    def get_options(self, path: str) -> list[str]:
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

    def start_process(self, map_path: str, turn_delay: float = 0.5) -> None:
        self._map = self.map_select(self.get_options(map_path))

        while not self._map.is_finished:
            self.process_turn(self._auto_advance_turns)
            if not self._auto_advance_turns:
                sleep(turn_delay)

    @abstractmethod
    def map_select(self, files: list[str]) -> Map:
        ...

    @abstractmethod
    def process_turn(self, auto_advance: bool) -> None:
        ...

    @abstractmethod
    def on_input(self) -> Any:
        ...
