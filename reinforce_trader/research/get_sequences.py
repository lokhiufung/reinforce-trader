import pandas as pd
import numpy as np


# turn df to sequences
def get_rolling_window_sequences(df: pd.DataFrame, window_size: int) -> np.ndarray:
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame.")

    num_rows, num_columns = df.shape
    if num_rows < window_size:
        raise ValueError(f'DataFrame must have more rows than {window_size=}: {num_rows=}')

    series = df.values

    # Calculate shape and strides for the rolling window
    shape = (num_rows - window_size + 1, window_size, num_columns)
    strides = (series.strides[0], series.strides[0], series.strides[1])

    return np.lib.stride_tricks.as_strided(series, shape=shape, strides=strides)

# Example usage:
# series = np.array([your_data_series])
# window_size = 5  # for example, a window size of 5
# sequences = rolling_window_sequences(series, window_size)
# print(sequences)