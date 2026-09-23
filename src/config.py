from src.render import TerminalRenderer, PygameRenderer, MapProcess
from argparse import Namespace, ArgumentParser
from src.utils import Logs


class Config:
    """ Configuration handler for the module. """

    def __init__(self) -> None:
        """ Parses arguments, sets up the logger and starts renderer. """

        self.args: Namespace = self._register_arguments()
        self.logs: Logs = Logs(
                write=self.args.write_logs,
                debug=self.args.debug)

        try:
            self._start_render(self.args.terminal)
        except Exception as e:
            print(e)

    def _start_render(self, do_terminal: bool = False) -> None:
        """
        Starts rendering process going through map selection first using
        selected rendering method.

        Args:
            do_terminal: Whether to use terminal rendering or not.
        """

        # TODO Add back in when pygame works
        # renderer: MapProcess = TerminalRenderer(self.logs) if do_terminal \
        #         else PygameRenderer(self.logs)
        renderer: MapProcess = TerminalRenderer(self.logs, self.args.no_auto)

        renderer.start_process(self.args.map_path)

    def _register_arguments(self) -> Namespace:
        """
        Sets up command-line arguments.

        Returns:
            Namespace: All registered arguments holding their values
                based on present flags.
        """

        arg_parser = ArgumentParser(
                prog="python -m src",
                description="Fly-in project made by Ilai. :)")

        _ = arg_parser.add_argument(
                "-m", "--map_path",
                help="Sets path to look for maps",
                default="maps/",
                required=False)

        ## TODO Implement write logs
        _ = arg_parser.add_argument(
                "-w", "--write_logs",
                help="Write simulation results to file simulation_results.txt",
                action="store_true",
                required=False)

        _ = arg_parser.add_argument(
                "-d", "--debug",
                help=("Adds useful debug info and writes it if "
                      "--write_logs is enabled "
                      "(live debug output only supported for terminal mode)"),
                action="store_true",
                required=False)

        _ = arg_parser.add_argument(
                "-t", "--terminal",
                help=("Switches to terminal output (default pygame)"),
                action="store_true",
                required=False)

        _ = arg_parser.add_argument(
                "-n", "--no_auto",
                help=("Turns off auto advancing on turns waiting for input "
                      "before continuing instead"),
                action="store_false",
                required=False)

        return arg_parser.parse_args()
