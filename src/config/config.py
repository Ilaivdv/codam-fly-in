from pydantic import BaseModel, PrivateAttr, ConfigDict
from .map_settings import MapSelector, MapError
from argparse import Namespace, ArgumentParser
from typing import Any


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
            self._map_selector.option_select(self._map_path)
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
