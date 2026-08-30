from pydantic import BaseModel, PrivateAttr, ConfigDict
from argparse import Namespace, ArgumentParser
from typing import Any
from .map_settings import MapSelector, MapError
import os


class ConfigError(Exception):
    """ Config error for verbosity """
    pass


class Config(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    _map_path: str = PrivateAttr()
    _map_selector: MapSelector = PrivateAttr(MapSelector())
    args: Namespace | None = None

    def model_post_init(self, _: Any, /) -> None:
        self.args = self._register_arguments()
        self._map_path = self.args.map_path
        try:
            print(self._map_selector.get_options(self._map_path))
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
