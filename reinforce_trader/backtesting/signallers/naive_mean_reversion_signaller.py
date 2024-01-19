
from reinforce_trader.backtesting.signallers.base_signaller import BaseSignaller


class NaiveMeanReversionSignaller(BaseSignaller):
    def __init__(self, prev_drop=0.05):
        self.prev_drop = prev_drop

    def get_signals(self, sequences):
        signals = (sequences[:, -2, -1] - sequences[:, -3, -1]) / sequences[:, -3, -1]
        return [1 if signal < self.prev_drop else 0 for signal in signals]
        