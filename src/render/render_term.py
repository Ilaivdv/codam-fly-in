from src.render.map_select import MapProcess
from colorama import Back, Fore, Style
from src.utils import Logs
from src.map import Map
import termios
import tty
import sys
import os


class TerminalRenderer(MapProcess):
    def __init__(self, logs: Logs) -> None:
        super().__init__(logs)

    def map_select(self, files: list[str]) -> Map:
        print(self._logs.__str__())
        selected: int = 0

        while True:
            print(f"\033c == {Fore.BLUE}Map Select{Fore.RESET} ==\n")
            for i, option in enumerate(files):
                if i == selected:
                    print(f"{Fore.GREEN}> {Back.WHITE}{Fore.BLACK}{
                          option}{Style.RESET_ALL}")
                    continue
                print(f" {option}")

            match self.on_input():
                case 'q':
                    print("\033c")
                    sys.exit()
                case 'h' | "left" | '\x7f' | '\x08':  # Also check backspace and del
                    # Go back a directory
                    return self.map_select(self.get_options(files[0].rsplit(
                        '/', 2)[0]))
                case 'j' | "down":
                    if selected < len(files) - 1:
                        selected += 1
                    else:
                        selected = 0
                case 'k' | "up":
                    if selected > 0:
                        selected -= 1
                    else:
                        selected = len(files) - 1
                case 'l' | "right" | '\r' :
                    # If it's a file, return the validated map
                    if files[selected].endswith(".txt"):
                        print("\033c")
                        return self._map_validator.validate_map(
                                    files[selected])
                    else:
                        for f in os.listdir(files[selected]):
                            if f.endswith(".txt"):
                                return self.map_select(
                                        self.get_options(files[selected]))
                case _:
                    pass

    def process_turn(self, auto_advance: bool) -> None:
        self._map.advance_turn()
        if len(self._logs.turns[-1]):
            if self._logs.debug:
                print(self._logs.turns_debug[-1])
            print(self._logs.turns[-1], end="\n\n")
        if not auto_advance:
            while True:
                match self.on_input():
                    case 'q':
                        sys.exit()
                    case '\r':
                        break
                    case _:
                        pass

    def on_input(self) -> str:
        original_settings = termios.tcgetattr(sys.stdin)
        try:
            _ = tty.setraw(sys.stdin.fileno())
            key: str = sys.stdin.read(1)
            if key == '\x1b':  # Escape sequence start
                # Read next two bytes to get escape sequence
                key += sys.stdin.read(2)
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
