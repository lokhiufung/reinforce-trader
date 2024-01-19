import typing
from abc import ABC, abstractmethod

import numpy as np


class Analyzer(ABC):
    name = None
    
    def __call__(self, input_array: np.ndarray, output_array: np.ndarray):
        analysis = self._run(input_array, output_array)
        return analysis

    @property
    def description(self) -> str:
        return """"""

    @abstractmethod
    def _run(self, input_array: np.ndarray, output_array: np.ndarray) -> dict:
        pass