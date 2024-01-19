from reinforce_trader.backtesting.signallers.base_signaller import BaseSignaller


class BuyAndHoldSignaller(BaseSignaller):
    
    def get_signals(self, sequences):
        length = len(sequences)
        signals = [0] * length
        signals[0] = 1
        signals[-1] = -1
        return signals