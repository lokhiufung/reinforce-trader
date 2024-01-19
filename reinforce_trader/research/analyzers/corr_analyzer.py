import numpy as np

from reinforce_trader.research.analyzers.analyzer import Analyzer


DESCRIPTION = """
This analyzer calculates the summary statistics about the correlations between the input array and output array.
It assumes the input array's and output array's dimension to be (number of samples, number of steps in the series, number of channels).
The output of the analyzer is a dictionary. Below is an example output:
####
{{0: {{'max': 0.9673702221571912,
    'mean': 0.6129416894353036,
    'median': 0.6419431433790508,
    'min': -0.2214063405700478,
    'q25': 0.5435060568673715,
    'q75': 0.7056128272572036}},
1: {{'max': 0.9670437842314047,
    'mean': 0.6051525037565001,
    'median': 0.6384623938372672,
    'min': -0.14736804591670732,
    'q25': 0.533118128497712,
    'q75': 0.7013030578206072}},
2: {{'max': 0.965834027107769,
    'mean': 0.6042959294029895,
    'median': 0.6384004341524272,
    'min': -0.3229204523199863,
    'q25': 0.5393103171245356,
    'q75': 0.7041330190133147}},
3: {{'max': 0.9668973472263083,
    'mean': 0.6119610735048845,
    'median': 0.6432652675452675,
    'min': -0.19261549248151896,
    'q25': 0.5457214023407723,
    'q75': 0.7058172257083992}},
}}
####
The keys are the index of the channels and the values are the summary statistics of the correlations (i.e maximum, mean, median, minimum, 25th quantile and 75 quantile) between the input array and output array in each channel.
"""


class CorrAnalyzer(Analyzer):
    name = 'corr_analyzer'

    @property
    def description(self):
        return DESCRIPTION
    
    def _run(self, input_array, output_array):
        # prepare a placeholder for each channel
        corrs = {channel: [] for channel in range(output_array.shape[2])}
        # assume dim to be (N, seq, channel)
        for i in range(output_array.shape[0]):
            for channel in range(output_array.shape[2]):
                x, y = input_array[i, :, channel], output_array[i, :, channel]
                n_nan = len(x) - len(y)
                corr = np.corrcoef(x[n_nan:], y)[0, 1]
                corrs[channel].append(corr)
        
        results = {}
        for channel in corrs:
            results[channel] = {}
            results[channel]['mean'] = np.mean(corrs[channel])
            results[channel]['median'] = np.median(corrs[channel])
            results[channel]['max'] = np.max(corrs[channel])
            results[channel]['min'] = np.min(corrs[channel])
            results[channel]['q75'] = np.quantile(corrs[channel], q=0.75)
            results[channel]['q25'] = np.quantile(corrs[channel], q=0.25)
        return results
        


                

