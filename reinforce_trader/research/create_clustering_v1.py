import numpy as np

from reinforce_trader.research.datalake_client import DatalakeClient
from reinforce_trader.research.feature_pipeline import FeaturePipeline
from reinforce_trader.research.models.kmeans_model_trainer import KmeansModelTrainer
from reinforce_trader.research.features.dct_feature import get_dct, get_dct_reconstruction
from reinforce_trader.research.features.standardizing_feature import get_log_and_standardized, get_minmax_scaling


def create_clustering_v1(hparams):
    # datalake_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
    dl_client = DatalakeClient()

    # initialize pipelines
    feature_pipeline = FeaturePipeline(
        pipeline=[
            lambda array: array[:, :, [3]], # use only the close price
            get_log_and_standardized,
            lambda array: array[:, :, 0], # use only the close price
            get_minmax_scaling,
            get_dct,
            get_dct_reconstruction,
        ],
        params={}
    )

    
    trainer = KmeansModelTrainer(
        hparams=hparams,
        dl_client=dl_client,
        feature_pipeline=feature_pipeline,
    )
    return trainer



def create_clustering_v1_from_model_ckpt_dir(model_ckpt_dir):
    # datalake_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
    dl_client = DatalakeClient()

    # initialize pipelines
    feature_pipeline = FeaturePipeline(
        pipeline=[
            lambda array: array[:, :, [3]], # use only the close price
            get_log_and_standardized,
            lambda array: array[:, :, 0], # use only the close price
            get_minmax_scaling,
            get_dct,
            get_dct_reconstruction,
        ],
        params={}
    )

    
    trainer = KmeansModelTrainer.from_model_ckpt(
        model_ckpt_dir,
        dl_client=dl_client,
        feature_pipeline=feature_pipeline,
    )
    return trainer
