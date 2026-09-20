from abc import ABC, abstractmethod


class State(ABC):
    """ A base state class. """

    @abstractmethod
    def on_enter(self) -> None:
        """ Handle events when state is entered. """
        pass

    @abstractmethod
    def on_event(self) -> None:
        """ Handle events for current state. """
        pass

    def __str__(self) -> str:
        """ Returns the name of the state. """
        return self.__class__.__name__
