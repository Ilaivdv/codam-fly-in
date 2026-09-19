class Logs:
    """
    Records logs for debugging and visualising of program.
    """

    def __init__(self, write: bool = False, debug: bool = False) -> None:
        self.write_logs: bool = write
        self.debug: bool = debug

        self._current_turn: str = ""
        self.turns: list[str] = []

    def log_drone_action(self, action: str) -> None:
        self._current_turn += " " + action

    def end_turn(self) -> None:
        self.turns.append(self._current_turn)
        self._current_turn = ""
