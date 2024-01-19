
from reinforce_trader.backtesting.strategies.base_strategy import BaseStrategy


class NaiveClusterStrategy(BaseStrategy):

    def __init__(self, stop_loss: float, take_profit: float, initial_balance: float, bet_size: float):
        super().__init__(initial_balance, bet_size)
        self.stop_loss = stop_loss
        self.take_profit = take_profit
    
    def on_bar(self, o, h, l, c, v, signal):
        action = 0
        if self.position == 0 and signal == 1:
            action = (self.bet_size * self.balance) // c
        if (self.position > 0) and (signal == -1 or ((self.avg_px - c) / self.avg_px >= self.stop_loss) or ((c - self.avg_px) / self.avg_px >= self.take_profit)):
            action =  -1 * self.position
        return action