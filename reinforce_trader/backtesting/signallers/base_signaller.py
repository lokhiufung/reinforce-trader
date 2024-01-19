from abc import ABC, abstractmethod

class BaseSignaller(ABC):

    def __init__(self, window_size: int):
        self._window_size = window_size

    @property
    def window_size(self):
        return self._window_size

    @abstractmethod
    def get_signals(self):
        """return a standardized signal to the strategy"""