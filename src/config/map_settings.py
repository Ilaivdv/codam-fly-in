import os

class MapError(Exception):
    """ Map error for verbosity """
    pass


class MapSelector:
    def get_options(self, path: str) -> list[str]:
        path = f"{os.getcwd()}/{path}"
        res: list[str] = []

        if not os.path.isdir(path):
            raise MapError(f"{path} is not a valid map directory")
        for i in os.listdir(path):
            i = path + i
            if not os.path.isdir(i) and not os.path.isfile(i):
                raise MapError(f"{i} is not a valid map directory/file")
            if i.endswith(".txt") or os.path.isdir(i):
                res.append(i)
        return res
