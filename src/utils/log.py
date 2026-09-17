from colorama import Fore


WARNING = f"{Fore.YELLOW}[WARNING]{Fore.RESET}"
ERROR = f"{Fore.RED}[ERROR]{Fore.RESET}"
DEBUG = "[DEBUG]"


class Logs:
    """
    Records logs for debugging and visualising of program.
    """
    def __init__(self, show: bool = False, write: bool = False) -> None:
        self.show_logs: bool = show
        self.write_logs: bool = write
        self.error_count: int = 0
        self.warning_count: int = 0
        self._events: list[tuple[str, str]] = []
        self._logo: str = ""

        if self.show_logs:
            with open("src/utils/logo.txt") as f:
                self._logo = f.read()

log: Logs
