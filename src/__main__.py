from .config import Config


def main() -> None:
    cfg = Config()
    cfg.args  # TODO Remove later, just to silence warnings


if __name__ == "__main__":
    main()
