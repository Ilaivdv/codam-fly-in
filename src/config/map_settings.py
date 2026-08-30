from pydantic import BaseModel, PrivateAttr
from colorama import Back, Fore, Style
import termios
import tty
import sys
import os


class MapError(Exception):
    """ Map error for verbosity """
    pass


class MapSelector(BaseModel):
    _map_options: list[str] = PrivateAttr()

    def _get_options(self, path: str) -> None:
        path += '/' if not path.endswith('/') else ''
        res: list[str] = []

        if not os.path.isdir(path) and not os.path.lexists(path):
            raise MapError(f"{path} is not a valid map directory")
        for i in os.listdir(path):
            i = path + i
            if not os.path.isdir(i) and not os.path.isfile(i):
                raise MapError(f"{i} is not a valid map directory/file")
            if i.endswith(".txt"):
                res.append(i)
            elif os.path.isdir(i):
                res.append(i + '/')
        self._map_options = res

    def option_select(self, path: str) -> None:
        self._get_options(path)

        def read_key() -> str:
            original_settings = termios.tcgetattr(sys.stdin)
            try:
                _ = tty.setraw(sys.stdin.fileno())
                key: str = sys.stdin.read(1)  # Read first byte
                if key == '\x1b':  # Escape sequence (special key)
                    # Read next two bytes (e.g., '[A' for Up)
                    key += sys.stdin.read(2)
                    # Map sequences to key names
                    key_map = {
                        '\x1b[A': 'up',
                        '\x1b[B': 'down',
                        '\x1b[C': 'right',
                        '\x1b[D': 'left'
                    }
                    return key_map.get(key, 'unknown')
                return key
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN,
                                  original_settings)

        selected: int = 0
        while True:
            print("\033c -- Press Q to quit\n")
            for i, option in enumerate(self._map_options):
                if i == selected:
                    print(Back.WHITE, option, Style.RESET_ALL)
                    continue
                print(option)

            key_pressed = read_key()
            if key_pressed == 'q':
                print("\033c")
                return
            elif key_pressed == '\r' or key_pressed == "right":
                self.option_select(self._map_options[selected])
                return
            elif key_pressed == "left":
                self.option_select(self._map_options[0].rsplit('/', 2)[0])
                return
            elif key_pressed == "down" and \
                    selected < len(self._map_options) - 1:
                selected += 1
            elif key_pressed == "up" and selected > 0:
                selected -= 1
