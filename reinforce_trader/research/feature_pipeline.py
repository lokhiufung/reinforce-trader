import typing
import inspect

import numpy as np

from reinforce_trader.research.features.feature import Feature
from reinforce_trader.research.analyzers.analyzer import Analyzer


class FeaturePipeline:

    def __init__(
            self,
            pipeline: typing.List[typing.Callable],
            params: typing.Dict[str, typing.Dict[str, typing.Any]],
            analyzers: typing.Optional[typing.Dict[str, typing.List[Analyzer]]]=None,
        ):
        self.params = params

        self._pipeline = []
        if analyzers is None:
            analyzers = {}
        for node in pipeline:
            if inspect.isclass(node) and issubclass(node, Feature):
                # initize the FeatureBlock, Analyzer if any
                feature_name = node.__name__
                params = self.params.get(feature_name, {})
                feature_analyzers = analyzers.get(feature_name, None)
                self._pipeline.append(node(analyzers=feature_analyzers, **params))
            else:
                self._pipeline.append(node)

    def _create_feature_pipeline_string(self) -> str:
        pipeline_structure_string = ''
        for i, node in enumerate(self._pipeline):
            number = i + 1
            analyzer_descriptions = '-'
            if isinstance(node, Feature):
                feature_name = node.__class__.__name__
                description = node.description
                if node.analyzers:
                    analyzer_descriptions = '\n'.join([f"""{analyzer.name}: {analyzer.description}""" for analyzer in node.analyzers])
            else:
                feature_name = node.__name__
                description = '-'
            feature_string = f"""
Feature number: {number}
Feature name: {feature_name}
Feature description: {description}
Analyzers:
----
{analyzer_descriptions}
----
"""
            pipeline_structure_string += feature_string + '\n'
        return pipeline_structure_string
    
    @property
    def description(self):
        pipeline_structure_string = self._create_feature_pipeline_string()
        description = f"""
The feature pipeline transforms a ndarray to another ndarray, which contains useful features to train a machine learning model.
There may be analyzers attached into the feature. These analyzer analyze the output array or the relation between input array and output array.

Here is the structure of the feature pipeline:
####
{pipeline_structure_string}
####
"""

        return description
    
    def run(self, array: np.ndarray):
        analysises_all = {}
        input_array = array.copy()
        for node in self._pipeline:
            try:
                # inspect and retrive the params from self.params
                if isinstance(node, Feature):
                    feature_name = node.__class__.__name__
                    output_array, analysises = node(input_array)
                    # check the dimension
                    is_correct, expected_shape = node.check_output_shape(input_array, output_array=output_array)
                    if not is_correct:
                        raise ValueError(f'Shapes do not match. feature_name={node.__class__} {expected_shape=} output_shape={output_array.shape} input_shape={input_array.shape}')
                else:
                    feature_name = node.__name__
                    params = self.params.get(feature_name, {})  # if no params specified, pass an empty dict
                    output_array = node(input_array, **params)
                    analysises = {}  # TODO: no analysis for functional node
                if analysises:
                    analysises_all[feature_name] = analysises
                # update the input_array
                input_array = output_array
            except:
                raise Exception(f'{feature_name=} {input_array.shape=}')
        return output_array, analysises_all



