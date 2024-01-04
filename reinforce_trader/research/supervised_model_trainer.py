from abc import ABC, abstractmethod
import typing

import numpy as np

from reinforce_trader.research.feature_pipeline import FeaturePipeline
from reinforce_trader.research.datalake_client import DatalakeClient
from reinforce_trader.research.sampler.sampler import Sampler


class SupervisedModelTrainer(ABC):
    def __init__(
            self,
            hparams: dict,
            dl_client: DatalakeClient,
            feature_pipeline: FeaturePipeline,
            label_pipeline: FeaturePipeline,
            sampler: Sampler=None,
        ):
        self.hparams = hparams
        self.dl_client = dl_client
        self.feature_pipeline = feature_pipeline
        self.label_pipeline = label_pipeline
        self.sampler = sampler
        self.datasets = {}
        self.analysises = {}

        if self.sampler is None:
            # use the default sampler -> no sampling
            self.sampler = Sampler()

    def get_data(self, key):
        if key not in self.datasets:
            self.datasets = self._get_datasets()
        
        data_feature, data_label = self.datasets[key]['feature'], self.datasets[key]['label'] 
        if key == 'train':
            data_feature, data_label = self.sampler.sample(x=data_feature, y=data_label)
            print(f'{data_feature.shape=} {data_label.shape=}')
        return data_feature, data_label
    
    @property
    def description(self):
        return
    
    @abstractmethod
    def _get_datasets(self) -> typing.Dict[str, typing.Dict[str, np.ndarray]]:
        """define your data pipeline workflow here"""

    def train(self, to_analyst: bool=False):
        # initialize the report for analyst
        report = {'model_analysises': {}}

        x_train, y_train = self.get_data('train')
        if self.sampler.analyzer and self.sampler.analyzer.name == 'dist_analyzer':
            # TEMP: analyze distribution of labels everytime?
            analysis = self.sampler.analyzer(y_train, y_train)
            report['sampler_analysises'] = {'dist_analyzer': analysis}
        model = self._train_step(x_train, y_train)
        x_test, y_test = self.get_data('test')
        report['model_analysises']['train'] = self._test_step(model, x_train, y_train)
        report['model_analysises']['test'] = self._test_step(model, x_test, y_test)
        # evaluation_report
        report['pipeline_analysises'] = self.analysises
        if to_analyst:
            report['descriptions'] = {
                'feature_pipeline': self.feature_pipeline.description,
                'label_pipeline': self.label_pipeline.description,
                'sampler': self.sampler.description,
                'model': self.description
            }
        return model, report

    # def test(self, report=True):
    #     x_train, y_train = self.get_data('train')
    #     model = self._train_step(x_train, y_train)
    #     report = {}
    #     if report:
    #         x_test, y_test = self.get_data('test')
    #         report['train'] = self._test_step(x_train, y_train)
    #         report['test'] = self._test_step(x_test, y_test)
    #         # evaluation_report
    #     return model, report
    
    @abstractmethod
    def _train_step(self, x: np.ndarray, y: np.ndarray):
        """a step to train"""

    @abstractmethod
    def _test_step(self, clf, x: np.ndarray, y: np.ndarray):
        """a step to test"""