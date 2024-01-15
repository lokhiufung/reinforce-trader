from abc import ABC, abstractmethod
import typing
import os

import numpy as np
import yaml
from joblib import dump, load

from reinforce_trader.research.feature_pipeline import FeaturePipeline
from reinforce_trader.research.datalake_client import DatalakeClient
from reinforce_trader.research.sampler.sampler import Sampler


class BaseModelTrainer(ABC):
    def __init__(
            self,
            hparams: dict,
            dl_client: DatalakeClient,
            feature_pipeline: FeaturePipeline,
            sampler: Sampler=None,
        ):
        self.hparams = hparams
        self.dl_client = dl_client
        self.feature_pipeline = feature_pipeline
        self.sampler = sampler
        self.datasets = {}
        self.analysises = {}

        self.model = None

        if self.sampler is None:
            # use the default sampler -> no sampling
            self.sampler = Sampler()

    def get_data(self, key) -> typing.Tuple[np.ndarray]:
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
        ...

    def train(self, to_analyst: bool=False):
        # initialize the report for analyst
        report = {}

        x_train, y_train = self.get_data('train')
        if self.sampler.analyzer and self.sampler.analyzer.name == 'dist_analyzer':
            # TEMP: analyze distribution of labels everytime?
            analysis = self.sampler.analyzer(y_train, y_train)
            report['sampler_analysises'] = {'dist_analyzer': analysis}
        self.model = self._train_step(x_train, y_train)
        # test
        report_test = self.test()
        report['model_analysises'] = report_test
        # evaluation_report
        report['pipeline_analysises'] = self.analysises
        if to_analyst:
            report['descriptions'] = {
                'feature_pipeline': self.feature_pipeline.description,
                'sampler': self.sampler.description,
                'model': self.description
            }
        return self.model, report

    def test(self):
        report_test = dict()
        if self.model is None:
            raise ValueError('model is not loaded')
        x_train, y_train = self.get_data('train')
        x_test, y_test = self.get_data('test')
        report_test['train'] = self._test_step(x_train, y_train)
        report_test['test'] = self._test_step(x_test, y_test)
        return report_test
        
    def test_step(self):
        ...

    @abstractmethod
    def _train_step(self, x: np.ndarray, y: np.ndarray):
        """a step to train"""

    @abstractmethod
    def _test_step(self, clf, x: np.ndarray, y: np.ndarray):
        """a step to test"""

    def save(self, model_ckpt_dir):
        if not os.path.exists(model_ckpt_dir):
            os.makedirs(model_ckpt_dir)
            
        # TODO: this is only valid for sklearn models
        model_file_path = os.path.join(model_ckpt_dir, 'model.joblib')
        hparams_file_path = os.path.join(model_ckpt_dir, 'hparams.yaml')
        dump(self.model, model_file_path)

        # write a yaml file
        with open(hparams_file_path, 'w') as f:
            yaml.safe_dump(self.hparams, f)
    
    @classmethod
    def from_model_ckpt(
        cls,
        model_ckpt_dir: str,
        dl_client: DatalakeClient,
        feature_pipeline: FeaturePipeline,
        sampler: Sampler=None,
    ):
        model_file_path = os.path.join(model_ckpt_dir, 'model.joblib')
        hparams_file_path = os.path.join(model_ckpt_dir, 'hparams.yaml')

        with open(hparams_file_path, 'r') as f:
            hparams = yaml.safe_load(f)
        
        trainer = cls(
            hparams,
            dl_client,
            feature_pipeline,
            sampler,
        )
        trainer.model = load(model_file_path)
        return trainer
