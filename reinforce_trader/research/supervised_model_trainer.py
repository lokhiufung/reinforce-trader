from abc import ABC, abstractmethod

import numpy as np

from reinforce_trader.research.feature_pipeline import FeaturePipeline
from reinforce_trader.research.datalake_client import DatalakeClient


class SupervisedModelTrainer(ABC):
    def __init__(
            self,
            hparams: dict,
            dl_client: DatalakeClient,
            feature_pipeline: FeaturePipeline,
            label_pipeline: FeaturePipeline,
        ):
        self.hparams = hparams
        self.dl_client = dl_client
        self.feature_pipeline = feature_pipeline
        self.label_pipeline = label_pipeline
        self.datasets = {}
        self.analysises = {}

    def get_data(self, key):
        if key not in self.datasets:
            self.datasets = self._get_data()
        return self.datasets[key]
    
    @property
    def description(self):
        return
    
    @abstractmethod
    def _get_data(self):
        """define your data pipeline workflow here"""

    def train(self, to_analyst: bool=False):
        data = self.get_data('train')
        x_train, y_train = data['feature'], data['label']
        model = self._train_step(x_train, y_train)
        report = {}
        test_data = self.get_data('test')
        x_test, y_test = test_data['feature'], test_data['label']
        report['train'] = self._test_step(model, x_train, y_train)
        report['test'] = self._test_step(model, x_test, y_test)
        # evaluation_report
        report['pipeline_analysises'] = self.analysises
        if to_analyst:
            report['descriptions'] = {
                'feature_pipelines': {
                    'feature': self.feature_pipeline.description,
                    'label': self.label_pipeline.description,
                },
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