import numpy as np

from reinforce_trader.research.analyzers.analyzer import Analyzer


class DistAnalyzer(Analyzer):
    name = 'dist_analyzer'

    def _run(self, input_array, output_array, label_col=0):

        if len(input_array.shape) > 0:
            # assume dimension to be (N, targets)
            labels = output_array[:, label_col]
        else:
            labels = output_array

        total = len(labels)
        # Calculate the frequency of each unique label
        unique, counts = np.unique(labels, return_counts=True)
        # Calculate the proportion of each label
        proportions = counts / total
        # Create a dictionary of label frequencies
        label_distribution = dict(zip(unique, proportions))
        return label_distribution