class Logs:
    """ Records logs for turns, debugging and visualising of program. """

    def __init__(self, write: bool = False, debug: bool = False) -> None:
        self.write_logs: bool = write
        self.debug: bool = debug

        self._current_turn: str = ""
        self._current_turn_debug: str = ""
        self.turns: list[str] = []
        self.turns_debug: list[str] = []

    def log_debug(self, msg: str) -> None:
        if self.debug:
            self._current_turn_debug += f"\n[DEBUG] {msg}"

    def log_drone_action(self, action: str) -> None:
        self._current_turn += " " + action

    def end_turn(self) -> None:
        self.turns_debug.append(self._current_turn_debug.strip())
        self._current_turn_debug = ""
        self.turns.append(self._current_turn.strip())
        self._current_turn = ""
