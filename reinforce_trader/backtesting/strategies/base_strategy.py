
from abc import ABC, abstractmethod


class BaseStrategy(ABC):

    def __init__(self, initial_balance, bet_size: float):
        self.balance = initial_balance
        self.bet_size = bet_size  # TODO: fraction of the balance, can be a function of (balance, signal)
        self.position = 0
        self.avg_px = None
    
    def get_balance(self):
        return self.balance
    
    def on_position_update(self, avg_px: float, position: float):
        self.avg_px = avg_px
        self.position = position

    def on_balance_update(self, balance: float):
        self.balance = balance
        
    @abstractmethod
    def on_bar(self, o, h, l, c, v, signal=None):
        """return the order action based on the bar (and signal [0, 1])"""