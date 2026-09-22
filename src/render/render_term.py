from src.render.map_select import MapProcess
from colorama import Back, Fore, Style
from src.utils import Logs
from src.map import Map
from enum import StrEnum
import termios
import tty
import sys
import os


class Colors(StrEnum):
    MAROON = "\033[38;2;85;0;0m"
    CRIMSON = "\033[38;2;220;20;60m"
    RED = "\033[38;2;255;0;0m"
    ORANGE = "\033[38;2;255;127;0m"
    BROWN = "\033[38;2;210;105;30m"
    GOLD = "\033[38;2;225;193;110m"
    YELLOW = "\033[38;2;255;255;120m"
    GREEN = "\033[38;2;0;255;143m"
    BLUE = "\033[38;2;90;156;255m"
    CYAN = "\033[38;2;0;230;255m"
    VIOLET = "\033[38;2;127;0;255m"
    PURPLE = "\033[38;2;128;0;128m"
    WHITE = "\033[38;2;255;255;255m"
    GRAY = "\033[38;2;90;90;90m"
    BLACK = "\033[38;2;0;0;0m"
    ## TODO Add rainbow function


class TerminalRenderer(MapProcess):
    def __init__(self, logs: Logs, auto_advance: bool = True) -> None:
        super().__init__(logs, auto_advance)

    def map_select(self, files: list[str]) -> Map:
        print(self._logs.__str__())
        selected: int = 0

        while True:
            print((f"\033c{Fore.LIGHTBLACK_EX} == Controls == {Fore.RESET}\n\n"
                   f" {Fore.LIGHTBLACK_EX}Q - Quit |"
                   " ←↓↑→/hjkl - Navigate |"
                   " Enter - Select |"
                   f" Backspace - Go back{Style.RESET_ALL}\n\n"
                   f" == {Fore.BLUE}Map Select{Fore.RESET} ==\n"))
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
                case 'h' | "left" | '\x7f' | '\x08':
                    # Go back a directory (also checks backspace and del)
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
                case 'l' | "right" | '\r':
                    # If it's a file, return the validated map
                    if files[selected].endswith(".txt"):
                        print(f"\n{Fore.LIGHTBLACK_EX}" +
                              f" Loading map...{Fore.RESET}", end="")
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

        def get_rainbow_text(text: str) -> str:
            rainbow: list[Colors] = [
                    Colors.RED,
                    Colors.ORANGE,
                    Colors.YELLOW,
                    Colors.GREEN,
                    Colors.CYAN,
                    Colors.BLUE,
                    Colors.PURPLE,
                    Colors.VIOLET
                    ]
            color: int = 0
            res: str = ""
            for c in text:
                res += rainbow[color] + c
                color = (color + 1) % len(rainbow)
            return res + Style.RESET_ALL

        if len(self._logs.turns[-1]):
            if self._logs.debug:
                print(self._logs.turns_debug[-1])

            action: list[str] = self._logs.turns[-1].split(" ")
            for i in action:
                split: list[str] = i.split("-")
                color: str = Colors.GRAY
                try:
                    zone_color: str = self._map.zones[split[1]].color.upper()
                    if zone_color == "RAINBOW":
                        print(f"{Colors.GRAY}{split[0]}-{
                              get_rainbow_text(split[1])}", end=" ")
                        continue
                    color = Colors[zone_color]
                except Exception:
                    pass
                print(f"{Colors.GRAY}{split[0]}-{
                      color}{split[1]}", end=" ")
            print(f"{Colors.GRAY}| T{len(self._logs.turns)}{Style.RESET_ALL}")

        # Listen for next action
        if not auto_advance:
            print(f"{Colors.GRAY}Waiting for input...{Style.RESET_ALL}")
            while True:
                match self.on_input():
                    case 'q':
                        sys.exit()
                    case '\r':
                        # Clear the temporary message first
                        print("\x1b[1A\x1b[2K", end="")
                        break
                    case _:
                        pass

    def on_process_finished(self) -> None:
        print(f"\n== {Colors.GREEN}Simulation finished in {
              len(self._logs.turns)} turns{Style.RESET_ALL} ==")

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
