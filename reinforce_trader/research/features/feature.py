import typing
from abc import ABC, abstractmethod

import numpy as np


class Feature(ABC):
    def __init__(self, analyzer=None):
        self.analyzer = analyzer
    
    @abstractmethod
    def check_output_shape(self, input_array: np.ndarray, output_array: np.ndarray) -> typing.Tuple[bool, tuple]:
        """check the output shape"""

    @abstractmethod
    def _run(self, array: np.ndarray) -> np.ndarray:
        """transformation on a array"""
        
    def __call__(self, input_array: np.ndarray) -> typing.Tuple[np.ndarray, dict]:
        output_array = self._run(input_array)
        if self.analyzer is not None:
            analysis = self.analyzer(input_array=input_array, output_array=output_array)
            analysis = {'analyzer_name': self.analyzer.name, 'analysis': analysis}
        else:
            analysis = None
        return output_array, analysis
        
    