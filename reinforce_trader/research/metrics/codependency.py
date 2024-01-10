# correlation codependence
import numpy as np
from scipy.stats import entropy

# correlation based
def get_corr_angular_dist(x, y):
    corr = np.corrcoef(x, y)[0, 1]
    return (0.5 * (1 - corr))**0.5



def get_corr_squared_dist(x, y):
    corr = np.corrcoef(x, y)[0, 1]
    return (1 - corr**2)**0.5


# information based
def discretize_series(s, bins=10):
    hist, bin_edges = np.histogram(s, bins=bins, density=True)
    digitized = np.digitize(s, bin_edges, right=True)
    return digitized, hist

def calculate_entropy(hist):
    probabilities = hist / hist.sum()
    probabilities = probabilities[probabilities > 0]  # Remove zero probabilities
    entropy = -np.sum(probabilities * np.log2(probabilities))
    return entropy

def get_mutual_information(s_1, s_2, bins=10):
    # Discretize both series
    s_1_digitized, _ = discretize_series(s_1, bins)
    s_2_digitized, _ = discretize_series(s_2, bins)

    # Joint histogram
    joint_hist = np.histogram2d(s_1_digitized, s_2_digitized, bins=bins)[0]

    # Convert joint histogram to probability
    joint_prob = joint_hist / np.sum(joint_hist)

    # Marginal probabilities
    prob_s_1 = np.sum(joint_prob, axis=1)
    prob_s_2 = np.sum(joint_prob, axis=0)

    # Calculate mutual information
    mi = 0
    for i in range(joint_prob.shape[0]):
        for j in range(joint_prob.shape[1]):
            if joint_prob[i, j] > 0:
                mi += joint_prob[i, j] * np.log2(joint_prob[i, j] / (prob_s_1[i] * prob_s_2[j]))

    return mi

def get_variation_of_information(s_1, s_2, bins=100, norm=False):
    # Discretize both series
    _, hist_1 = discretize_series(s_1, bins)
    _, hist_2 = discretize_series(s_2, bins)

    entropy_1 = calculate_entropy(hist_1)
    entropy_2 = calculate_entropy(hist_2)
    mutual_info = get_mutual_information(s_1, s_2, bins)

    vi = entropy_1 + entropy_2 - 2 * mutual_info
    if norm:
        vi /= (entropy_1 + entropy_2)
    # to avoid out of boundary
    # we estimate the entropy only by discretizing the series. The error depends on the bin size.
    if vi > 1:
        vi = 1.0
    if vi < 0:
        vi = 0.0
    return vi

