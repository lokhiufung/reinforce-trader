from reinforce_trader.backtesting.strategies.base_strategy import BaseStrategy


class BuyAndHoldStrategy(BaseStrategy):

    def on_bar(self, o, h, l, c, v, signal):
        if signal == 1:
            # all-in with a given bet size at the beginning
            return (self.bet_size * self.balance) // c
        elif signal == -1:
            # sell all assets = clear position
            return -1 * self.position
        else:
            return 0
            
        
