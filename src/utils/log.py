class Logs:
    """ Records logs for turns, debugging and visualization of the program. """

    def __init__(self, write: bool = False, debug: bool = False) -> None:
        """
        Initializes Logs.

        Args:
            write: Command-line argument for whether to write results to file.
            debug: Command-line argmuent for showing debug information.
        """

        self.write_logs: bool = write
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
