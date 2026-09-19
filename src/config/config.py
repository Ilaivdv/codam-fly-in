from src.config.parsing import MapSelector
from argparse import Namespace, ArgumentParser
from src.utils import Logs
from src.map import Map


## TODO Maybe move remove config directory and just move this outside
class Config:
    def __init__(self) -> None:
        self._map_selector: MapSelector = MapSelector()
        self._map: Map
        self.args: Namespace = self._register_arguments()
        self.log: Logs = Logs(
                write=self.args.write_logs,
                debug=self.args.debug)

        try:
            # Initialize map and process it before visualization
            self._map = self._map_selector.option_select(self.args.map_path)
            ## TODO Add logger to map
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
                "-w", "--write_logs",
                help="Write simulation results to file simulation_results.txt",
                action="store_true",
                required=False)

        return arg_parser.parse_args()
