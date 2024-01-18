from reinforce_trader.backtesting.strategies.base_strategy import BaseStrategy


class BuyAndHoldStrategy(BaseStrategy):

    def on_bar(self, o, h, l, c, v, signal):
        if signal == 1:
            return self.bet_size
        elif signal == 0:
            return -1 * self.bet_size
        
