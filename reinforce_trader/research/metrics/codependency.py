# correlation codependence
import numpy as np
from scipy.stats import entropy


def get_corr_angular_dist(x, y):
    corr = np.corrcoef(x, y)[0, 1]
    return (0.5 * (1 - corr))**0.5



def get_corr_squared_dist(x, y):
    corr = np.corrcoef(x, y)[0, 1]
    return (1 - corr**2)**0.5

