import numpy as np

from reinforce_trader.research.features.feature import Feature


DESCRIPTION = """
This feature produce label, and actual_return of the input array.
It assumes the input array's dimension to be (number of samples, number of steps, number of channels).
It assumes that channels represent the `open`, `high`, `low` and `close` price of each step.
The output of the feature is a ndarray. Below is an example output:
####
[
    [-1.0, 1.2],
    [-1.0, 3.2],
    [1.0, -0.06],
    [1.0, -4.7],
    [0.0, 1.2],
    ...
]
####
The dimension of the output array is (number of samples, 2), where the last dimension represents the label and actural return
"""


class TripleBarrierFeature(Feature):
    def __init__(self, r_stop: float, r_take: float, analyzers=None):
        self.r_stop = r_stop
        self.r_take = r_take
        super().__init__(analyzers=analyzers)

    @property
    def description(self):
        return DESCRIPTION
    
    def check_output_shape(self, input_array: np.ndarray, output_array: np.ndarray):
        expected_shape = (input_array.shape[0], 2)  # (N, label_and_return)
        is_correct = output_array.shape == expected_shape
        return is_correct, expected_shape

    def _run(self, array):
        """
        Labels each sequence in a numpy array of OHLC sequences.

        Args:
            ohlc_sequences (np.array): Numpy array where each row is an OHLC sequence.
            r_stop (float): Percentage loss for stop loss.
            r_take (float): Percentage gain for take profit.
            T (int): Horizon of trading (number of steps in each sequence).

        Returns:
            np.array: Array of labels (1 for take profit, -1 for stop loss, 0 for end of the horizon).
        """
        labels = []

        for sequence in array:
            entry_price = sequence[0, 0]  # Open price of the first day in the sequence. Assume you get the signal last night and buy in the morning of the market
            take_profit_price = entry_price * (1 + self.r_take)
            stop_loss_price = entry_price * (1 - self.r_stop)

            label = 0  # Default label (hold till end of horizon)
            final_price = sequence[-1, 3]  # Close price of the last day in the sequence

            for day in sequence:
                day_high = day[1]  # High price of the day
                day_low = day[2]  # Low price of the day

                if day_high >= take_profit_price:
                    label = 1  # Take profit
                    final_price = take_profit_price
                    break
                elif day_low <= stop_loss_price:
                    label = -1  # Stop loss
                    final_price = stop_loss_price
                    break

            actual_return = final_price - entry_price
            labels.append((label, actual_return))

        return np.array(labels)

# Example usage:
# ohlc_sequences = np.array([[your_ohlc_data]])  # Replace with your OHLC data
# r_stop = 0.02  # Example stop loss percentage
# r_take = 0.03  # Example take profit percentage
# T = 5  # Trading horizon
# labels = label_ohlc_sequences(ohlc_sequences, r_stop, r_take, T)
# print(labels)
