from argparse import Namespace, ArgumentParser
from .parsing import MapSelector, ParseError
from colorama import Fore
from src import Map, Process


class Config:
    def __init__(self) -> None:
        self._map_selector: MapSelector = MapSelector()
        self._map: Map
        self.args: Namespace = self._register_arguments()

        try:
            # Initialize map through option_select selected file
            self._map = self._map_selector.option_select(self.args.map_path)
            if not self._map:
                raise ParseError((f"\n{Fore.RED}Error{Fore.RESET}: "
                                 "invalid map configuration"))
        except ParseError as e:
            print(e)

        self._process: Process = Process(self._map)


    def _register_arguments(self) -> Namespace:
        arg_parser = ArgumentParser(
                prog="python -m src",
                description="Fly-in project made by Ilai. :)")

        _ = arg_parser.add_argument(
                "-m", "--map_path",
                help="Sets path to look for maps.",
                default="maps/",
                required=False)

        _ = arg_parser.add_argument(
                "-w", "--write-logs",
                help="Write simulation results to file result.txt",
                default="maps/",
                required=False)

        return arg_parser.parse_args()
