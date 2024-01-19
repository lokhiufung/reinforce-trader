from reinforce_trader.research.analyzers.analyzer import Analyzer
from reinforce_trader.research.stats.stationarity import perform_adf_test


DESCRIPTION = """
This analyzer tests the autocorrelations (using the ADF test) in the output array.
It assumes the output array's dimension to be (number of samples, number of steps in the series, number of channels).
The output of the analyzer is a dictionary. Below is an example output:
####
{{
    0: {{'not_rejected': 1205,
    'percentage_rejected': 45.52441229656419,
    'rejected': 1007}},
    1: {{'not_rejected': 1369,
        'percentage_rejected': 38.11030741410488,
        'rejected': 843}},
    2: {{'not_rejected': 1354,
        'percentage_rejected': 38.78842676311031,
        'rejected': 858}},
    3: {{'not_rejected': 1176,
        'percentage_rejected': 46.835443037974684,
        'rejected': 1036}}
}},
####
The keys are the index of the channels and the values are the ADF test results (number of tests that are not rejected, number of tests that are rejected and the percentage of tests that are rejected) on the output array for each channel.
"""


class AutocorrAnalyzer(Analyzer):
    name = 'autocorr_analyzer'

    def __init__(self, alpha=0.05):
        super().__init__()
        self.alpha = alpha

    def description(self):
        return DESCRIPTION
    
    def _run(self, input_array, output_array):
        # prepare a placeholder for each channel
        results = {channel: {'rejected': 0, 'not_rejected': 0} for channel in range(output_array.shape[2])}
        # assume dim to be (N, seq, channel)
        for i in range(output_array.shape[0]):
            for channel in range(output_array.shape[2]):
                result = perform_adf_test(output_array[i, :, channel])
                if result['p-value'] < self.alpha:
                    results[channel]['rejected'] += 1
                else:
                    results[channel]['not_rejected'] += 1
        # aggregate results
        for channel in results:
            results[channel]['percentage_rejected'] = 100 * (results[channel]['rejected'] / output_array.shape[0])
        return results
        


                

