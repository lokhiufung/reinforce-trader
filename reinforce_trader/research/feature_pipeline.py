import typing
import inspect

import numpy as np

from reinforce_trader.research.features.feature_block import FeatureBlock 


class FeaturePipeline:

    def __init__(self, pipeline: typing.List[typing.Callable], params: typing.Dict[str, typing.Dict[str, typing.Any]]):
        self.params = params

        self._pipeline = []
        for feature in pipeline:
            if inspect.isclass(feature) and issubclass(feature, FeatureBlock):
                # initize the FeatureBlock if any
                feature_block_name = feature.__name__
                params = self.params.get(feature_block_name, {})
                self._pipeline.append(feature(**params))
            else:
                self._pipeline.append(feature)

    def run(self, array: np.ndarray):
        input_array = array.copy()
        for feature in self._pipeline:
            # inspect and retrive the params from self.params
            if isinstance(feature, FeatureBlock):
                output_array = feature(input_array)
                # check the dimension
                is_correct, expected_shape = feature.check_output_shape(input_array, output_array=output_array)
                if not is_correct:
                    raise ValueError(f'Shapes do not match. feature_name={feature.__class__} {expected_shape=} output_shape={output_array.shape} input_shape={input_array.shape}')
            else:
                feature_name = feature.__name__
                params = self.params.get(feature_name, {})  # if no params specified, pass an empty dict
                output_array = feature(input_array, **params)
            # update the input_array
            input_array = output_array
        return output_array



