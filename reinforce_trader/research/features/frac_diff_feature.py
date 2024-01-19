import numpy as np

from reinforce_trader.research.features.feature import Feature


def get_weights(d: float, size: int) -> np.ndarray:
    # Weights for fractional differentiation
    # the series of weights is a binomail series?
    w = [1.]
    for k in range(1, size):
        w.append(-w[-1] * ((d - k + 1)) / k)
    w = np.array(w[::-1]).reshape(-1, 1)
    return w


def frac_diff(array: np.ndarray, d: float, threshold=0.01) -> np.ndarray:
    """
    Applies fractional differentiation to a time series.
    This refers to the Fixed-Width window fracdiff

    :param array: A time series data.
    :param d: Fractional d (d).
    :param threshold: Cutoff threshold for weights.
    :return: Fractionally differentiated series.
    """
    # Length of the time series
    array_length = len(array)

    # Getting the weights
    weights = get_weights(d, array_length)

    # Adjust weights for threshold
    weights = np.array(weights[np.abs(weights) > threshold])
    diff_series_length = array_length - len(weights) + 1

    # Applying the weights to the series
    diff_series = []
    for i in range(diff_series_length):
        window = array[i:i + len(weights)]

        # Handle scalar result of np.dot
        result = np.dot(weights.T, window)
        if np.isscalar(result):
            diff_series.append(result)
        else:
            diff_series.append(result[0])

#     diff_series = pd.Series(diff_series, index=series.index[-diff_series_length:])
    return np.array(diff_series)


DESCRIPTION = """
This feature produce fractionally differentiated series of the input array for each channel.
It assumes the input array's dimension to be (number of samples, number of steps, number of channels).
The output of the feature is a ndarray. Below is an example output:
####
[
    [[100.1, 120.5, 109.4, 104.2], [101.1, 110.5, 109.2, 106.2], ...],
    [[102.1, 121.5, 100.4, 102.2], [101.1, 110.5, 109.2, 106.2], ...],
    ...
]
####
The dimension of the output array is (number of samples, number of steps after differentated fractionally, number of channels).
"""


class FracDiffMultiChannelFeature(Feature):
    def __init__(self, d, threshold=0.01, analyzers=None):
        self.d = d
        self.threshold = threshold
        super().__init__(analyzers=analyzers)
    
    @property
    def description(self):
        return DESCRIPTION
    
    def check_output_shape(self, input_array: np.ndarray, output_array: np.ndarray):
        weights = get_weights(self.d, size=input_array.shape[1])
        weights = np.array(weights[np.abs(weights) > self.threshold])

        expected_shape = (input_array.shape[0], input_array.shape[1] - len(weights) + 1, input_array.shape[2])

        is_correct = output_array.shape == expected_shape
        return is_correct, expected_shape
            
    def _run(self, array: np.ndarray) -> np.ndarray:
        """
        TODO: better do it with broadcasting
        Assume array is a (N, seq, channels) array
        """
        array_result = []
        for i in range(array.shape[0]):
            array_channels = []
            for channel in range(array.shape[2]):
                array_channel = frac_diff(array[i, :, channel], self.d, self.threshold)
                array_channels.append(array_channel)
            array_channels = np.array(array_channels).T  # from (channel, seq) to (seq, channel)
            array_result.append(array_channels)
        return np.array(array_result)
        