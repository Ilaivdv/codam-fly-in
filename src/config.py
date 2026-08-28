
class ConfigError(Exception):
    ...

class Config:
    def __init__(self) -> None:
        pass

    def get_maps_path(self) -> str:
        ...
