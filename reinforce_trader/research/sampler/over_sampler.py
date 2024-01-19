import numpy as np
from collections import Counter

from reinforce_trader.research.sampler.sampler import Sampler


DESCRIPTION = """
This sampler produce a balanced training data (based on their labels) using over-sampling technique.
It assumes 2 input numpy arrays x and y, where y is a (number of samples, ) array containing the labels.
The output of the sampler is a balanced training data, which is a tuple of sampled x and y (i.e numpy array).
"""


class OverSampler(Sampler):

    @property
    def description(self):
        return DESCRIPTION
    
    def sample(self, x: np.ndarray, y: np.ndarray):
        # Count the occurrences of each class
        class_counts = Counter(y)
        
        # Find the majority class count
        max_count = max(class_counts.values())

        # Initialize lists to hold the oversampled X and Y
        x_oversampled, y_oversampled = [], []

        # Loop over each class and oversample if necessary
        for class_label in class_counts:
            # Indices of the current class
            class_indices = np.where(y == class_label)[0]

            # Number of samples to generate for the current class
            samples_to_generate = max_count - class_counts[class_label]

            # Randomly select samples from the current class
            oversampled_indices = np.random.choice(class_indices, samples_to_generate, replace=True)

            # Combine original and oversampled indices for the current class
            combined_indices = np.concatenate([class_indices, oversampled_indices])

            # Append the current class's samples (original and oversampled) to the overall lists
            x_oversampled.extend(x[combined_indices])
            y_oversampled.extend(y[combined_indices])

        return np.array(x_oversampled), np.array(y_oversampled)

# Example usage:
# x, y = load_your_data() # load your data here
# oversampler = OverSampler()
# x_balanced, y_balanced = oversampler.sample(x, y)
