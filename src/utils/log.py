import atexit
import os

class Logs:
    """ Records logs for turns, debugging and visualization of the program. """

    def __init__(self, write: str = "", debug: bool = False) -> None:
        """
        Initializes Logs.

        Args:
            write: Command-line argument for file to write results to.
                (default empty)
            debug: Command-line argmuent for showing debug information.
        """

        self.write_file: str = write
        _ = atexit.register(self._write_logs)
        self.debug: bool = debug

        self._current_turn: str = ""
        self._current_turn_debug: str = ""
        self.turns: list[str] = []
        self.turns_debug: list[str] = []

    def log_debug(self, msg: str) -> None:
        """ Logs given message to debug logs. """

        if self.debug:
            self._current_turn_debug += f"\n[DEBUG] {msg}"

    def log_drone_action(self, action: str) -> None:
        """ Logs given Drone movement to _current_turn """

        self._current_turn += " " + action

    def end_turn(self) -> None:
        """
        Ends current turn, joining _current_turn to one string and
        appending it to list of total turns,
        does the same for debug messages.
        """

        self.turns_debug.append(self._current_turn_debug.strip())
        self._current_turn_debug = ""
        self.turns.append(self._current_turn.strip())
        self._current_turn = ""

    def _write_logs(self) -> None:
        """
        Writes logs to given argument from flag write_logs,
        otherwise does nothing.
        """

        if not self.write_file:
            return
        if "/" in self.write_file:
            os.makedirs(os.path.dirname(self.write_file), exist_ok=True)
        with open(self.write_file, "w") as f:
            for i, turn in enumerate(self.turns):
                if self.debug:
                    _ = f.write(self.turns_debug[i] + "\n")
                _ = f.write((f"Turn {i + 1}:" if self.debug else "") +
                             f" {turn}\n\n")
