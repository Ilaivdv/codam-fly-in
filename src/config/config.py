from argparse import Namespace, ArgumentParser
from .parsing import MapSelector, ParseError
from colorama import Fore
from typing import Any
from src import Map


class Config:
    def __init__(self) -> None:
        self._map_selector: MapSelector = MapSelector()
        self.map: Map
        self.args: Namespace = self._register_arguments()

        try:
            # Initialize map through option_select selected file
            self.map = self._map_selector.option_select(self.args.map_path)
            if not self.map:
                raise ParseError((f"\n{Fore.RED}Error{Fore.RESET}: "
                                "invalid map configuration"))
            self.start()
        except ParseError as e:
            print(e)

    def start(self) -> None:
        self.map.map_distances()

    def _register_arguments(self) -> Namespace:
        arg_parser = ArgumentParser(
                prog="python -m src",
                description="Fly-in project made by Ilai. :)")

        _ = arg_parser.add_argument(
                "-m", "--map_path",
                help="Sets path to look for maps.",
                default="maps/",
                required=False)

        return arg_parser.parse_args()
