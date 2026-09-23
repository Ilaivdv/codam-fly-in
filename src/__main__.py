"""
This is the modules entry point.

Since the project requires it to be fully object-oriented,
it only initializes the Config class which does all the required setup
to run the program.
"""

from src.config import Config


def main() -> None:
    """ Initializes Config class. """

    _ = Config()


if __name__ == "__main__":
    main()
