from src.config.parsing import MapSelector
from argparse import Namespace, ArgumentParser
from src.map import Map


class Config:
    def __init__(self) -> None:
        self._map_selector: MapSelector = MapSelector()
        self._map: Map
        self.args: Namespace = self._register_arguments()

        try:
            # Initialize map and process it before visualization
            self._map = self._map_selector.option_select(self.args.map_path)
            self._map.process()
        except Exception as e:
            print(e)

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
