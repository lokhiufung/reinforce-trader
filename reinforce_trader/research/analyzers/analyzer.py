import typing
from abc import ABC, abstractmethod

import numpy as np


class Analyzer(ABC):
    name = None
        
    def __call__(self, input_array, output_array):
        return self._run(input_array, output_array)

    @abstractmethod
    def _run(self, input_array, output_array) -> typing.Tuple[dict]:
        pass