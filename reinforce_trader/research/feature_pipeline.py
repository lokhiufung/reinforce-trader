import typing
import inspect

import numpy as np

from reinforce_trader.research.features.feature import Feature
from reinforce_trader.research.analyzers.analyzer import Analyzer


class FeaturePipeline:

    def __init__(self, pipeline: typing.List[typing.Callable], params: typing.Dict[str, typing.Dict[str, typing.Any]], analyzers: typing.Optional[typing.Dict[str, Analyzer]]=None):
        self.params = params

        self._pipeline = []
        if analyzers is None:
            analyzers = {}
        for node in pipeline:
            if inspect.isclass(node) and issubclass(node, Feature):
                # initize the FeatureBlock, Analyzer if any
                feature_name = node.__name__
                params = self.params.get(feature_name, {})
                analyzer = analyzers.get(feature_name, None)
                self._pipeline.append(node(analyzer=analyzer, **params))
            else:
                self._pipeline.append(node)

    def run(self, array: np.ndarray):
        analysises = {}
        input_array = array.copy()
        for node in self._pipeline:
            # inspect and retrive the params from self.params
            if isinstance(node, Feature):
                feature_name = node.__class__.__name__
                output_array, analysis = node(input_array)
                # check the dimension
                is_correct, expected_shape = node.check_output_shape(input_array, output_array=output_array)
                if not is_correct:
                    raise ValueError(f'Shapes do not match. feature_name={node.__class__} {expected_shape=} output_shape={output_array.shape} input_shape={input_array.shape}')
            else:
                feature_name = node.__name__
                params = self.params.get(feature_name, {})  # if no params specified, pass an empty dict
                output_array = node(input_array, **params)
                analysis = None  # TODO: no analysis for functional node
            if analysis is not None:
                analysises[feature_name] = analysis
            # update the input_array
            input_array = output_array
        return output_array, analysises



