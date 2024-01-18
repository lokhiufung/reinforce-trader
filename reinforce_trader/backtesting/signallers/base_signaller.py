from abc import ABC, abstractmethod

class BaseSignaller(ABC):

    @abstractmethod
    def get_signals(self):
        """return a standardized signal to the strategy"""