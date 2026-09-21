from argparse import Namespace, ArgumentParser
from src.render import TerminalRenderer
from src.utils import Logs


class Config:
    def __init__(self) -> None:
        self.args: Namespace = self._register_arguments()
        self.logs: Logs = Logs(
                write=self.args.write_logs,
                debug=self.args.debug)

        try:
            ...
        except Exception as e:
            print(e)

    # def _init_render(self, which: )

    def _register_arguments(self) -> Namespace:
        arg_parser = ArgumentParser(
                prog="python -m src",
                description="Fly-in project made by Ilai. :)")

        _ = arg_parser.add_argument(
                "-m", "--map_path",
                help="Sets path to look for maps",
                default="maps/",
                required=False)

        _ = arg_parser.add_argument(
                "-w", "--write_logs",
                help="Write simulation results to file simulation_results.txt",
                action="store_true",
                required=False)

        _ = arg_parser.add_argument(
                "-d", "--debug",
                help=("Adds useful debug info and writes it if"
                      "--write_logs is enabled "
                      "(live output only supported for terminal mode)"),
                action="store_true",
                required=False)

        return arg_parser.parse_args()
