import os

import numpy as np

from reinforce_trader.research.datalake_client import DatalakeClient
from reinforce_trader.research.feature_pipeline import FeaturePipeline
from reinforce_trader.research.features import FracDiffMultiChannelFeature, TripleBarrierFeature
from reinforce_trader.research.models.random_forest_model_trainer import RandomForesModelTrainer
from reinforce_trader.research.analyzers import DistAnalyzer, CorrAnalyzer 
from reinforce_trader.research.sampler.over_sampler import OverSampler


def create_classifier_v1(hparams):
    # datalake_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
    dl_client = DatalakeClient()

    # initialize pipelines
    feature_pipeline = FeaturePipeline(
        pipeline=[
            np.log,
            FracDiffMultiChannelFeature,
            lambda array: array.reshape(array.shape[0], -1),  # flatten the last 2 dimensions (seq * channel)
            # lambda array: array[:, :, 0].reshape(array.shape[0], -1),  # flatten the last 2 dimensions (seq * channel)
        ],
        params={
            'FracDiffMultiChannelFeature': {'d': hparams['feature_pipeline']['d'], 'threshold': hparams['feature_pipeline']['threshold']}
        },
        analyzers={
            'FracDiffMultiChannelFeature': [CorrAnalyzer()]
        }
    )

    label_pipeline = FeaturePipeline(
        pipeline=[
            TripleBarrierFeature,
            lambda array: array[:, 0],  # use the labels only 
        ],
        params={
            'TripleBarrierFeature': {'r_stop': hparams['label_pipeline']['r_stop'], 'r_take': hparams['label_pipeline']['r_take']}
        },
        # analyzers={
        #     'TripleBarrierFeature': [DistAnalyzer()]  # TODO: only Feature can use analyzer
        # }
    )

    trainer = RandomForesModelTrainer(
        hparams=hparams,
        dl_client=dl_client,
        feature_pipeline=feature_pipeline,
        label_pipeline=label_pipeline,
        sampler=OverSampler(analyzer=DistAnalyzer()),
    )
    return trainer
