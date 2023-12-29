import numpy as np

from reinforce_trader.research.analyzers.analyzer import Analyzer


DESCRIPTION = """
This analyzer tests the (discrete) distribution of the output array.
It assumes the output array's dimension to be (number of samples, ), where the there are finite number of distinct values (C).
The output of the analyzer is a dictionary. Below is an example output:
####
{{
    -1.0: 0.5682640144665461,
    0.0: 0.09584086799276673,
    1.0: 0.3358951175406872
}}
####
The keys are the index of the channels and the values are the ADF test results (number of tests that are not rejected, number of tests that are rejected and the percentage of tests that are rejected) on the output array for each channel.
"""


class DistAnalyzer(Analyzer):
    name = 'dist_analyzer'

    def __init__(self, label_col=0):
        super().__init__()
        self.label_col = label_col

    @property
    def description(self):
        return DESCRIPTION

    def _run(self, input_array, output_array):

        if len(input_array.shape) > 0:
            # assume dimension to be (N, targets)
            labels = output_array[:, self.label_col]
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