from pydantic import BaseModel, PrivateAttr, ConfigDict
from .map_settings import MapSelector, MapError
from colorama import Fore
from argparse import Namespace, ArgumentParser
from typing import Any
from src import Map


class ConfigError(Exception):
    """ Config error for verbosity """
    pass


class Config(BaseModel):
    # Setting arbitrary_types_allowed to allow custom classes as type hint
    model_config = ConfigDict(arbitrary_types_allowed=True)
    _map_selector: MapSelector = PrivateAttr(MapSelector())
    args: Namespace | None = None
    map: Map | None = None

    def model_post_init(self, _: Any, /) -> None:
        self.args = self._register_arguments()
        try:
            self.map = self._map_selector.option_select(self.args.map_path)
            if not self.map:
                raise MapError((f"\n{Fore.RED}Error{Fore.RESET}: "
                                "invalid map configuration"))
        except MapError as e:
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

        return arg_parser.parse_args()
