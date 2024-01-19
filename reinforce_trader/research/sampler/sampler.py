
import typing
import numpy as np

from reinforce_trader.research.analyzers.analyzer import Analyzer


class Sampler:
    def __init__(self, seed=0, analyzer: Analyzer=None):
        self.seed = seed
        self.analyzer = analyzer

    @property
    def description(self) -> str:
        return """
This is the base sample which do no sampling at all.
It just returns the same dataset.
"""
    
    def sample(self, x: np.ndarray, y: np.ndarray) -> typing.Tuple[np.ndarray]:
        return x, y

