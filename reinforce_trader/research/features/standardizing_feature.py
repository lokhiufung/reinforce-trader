import numpy as np


def get_log_and_standardized(input_sequences: np.ndarray):
    # Extract the first timestep across all sequences for normalization
    first_timesteps = input_sequences[:, 0, 0]
    
    # Perform the log transformation and normalization in a vectorized manner
    transformed_sequences = np.log(input_sequences[:, :, 0]) - np.log(first_timesteps)[:, None]
    
    # Reshape the output to add the third dimension back
    return transformed_sequences[..., np.newaxis]


def get_minmax_scaling(time_series_array: np.ndarray):
    # Calculate the min and max for each time series (along the second axis)
    ts_min = np.min(time_series_array, axis=1, keepdims=True)
    ts_max = np.max(time_series_array, axis=1, keepdims=True)
    
    # Compute the range and avoid division by zero by adding a small number
    ts_range = np.maximum(ts_max - ts_min, 1e-8)
    
    # Apply min-max scaling
    time_series_normalized = (time_series_array - ts_min) / ts_range
    
    return time_series_normalized
