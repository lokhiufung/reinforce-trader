
from abc import ABC, abstractmethod


class BaseStrategy(ABC):

    def __init__(self, bet_size):
        self.bet_size = bet_size  # TODO: can be a function of (balance, signal)
    
    @abstractmethod
    def on_bar(self, o, h, l, c, v, signal=None):
        """return the order action based on the bar (and signal [0, 1])"""