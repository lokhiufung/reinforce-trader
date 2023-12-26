from abc import ABC, abstractmethod

import numpy as np


class FeatureBlock(ABC):

    @abstractmethod
    def check_output_shape(self, input_array: np.ndarray, output_array: np.ndarray):
        """check the output shape"""
        
