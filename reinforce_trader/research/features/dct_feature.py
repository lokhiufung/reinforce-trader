import numpy as np
from scipy.fftpack import dct, idct


def get_dct(time_series_array):
    # Apply DCT to each time series along the last axis (number of steps)
    time_series_dct = dct(time_series_array, axis=1, norm='ortho')
    return time_series_dct


def get_dct_reconstruction(time_series_dct, keep_percentage=0.1):
    # Initialize the array to hold the thresholded DCT coefficients
    dct_thresholded = np.zeros_like(time_series_dct)
    
    # Determine the number of coefficients to keep for each series
    n_coefficients_to_keep = np.int32(keep_percentage * time_series_dct.shape[1])
    
    # For each time series, find the indices of the largest coefficients
    indices = np.argsort(-np.abs(time_series_dct), axis=1)[:, :n_coefficients_to_keep]
    
    # Use numpy's advanced indexing to zero out all but the significant DCT coefficients
    row_indices = np.arange(time_series_dct.shape[0])[:, None]
    dct_thresholded[row_indices, indices] = time_series_dct[row_indices, indices]
    
    # Reconstruct the signal from the modified DCT coefficients
    reconstructed_signal = idct(dct_thresholded, axis=1, norm='ortho')
    
    return reconstructed_signal
