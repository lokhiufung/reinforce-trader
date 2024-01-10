import numpy as np

from reinforce_trader.research.datalake_client import DatalakeClient
from reinforce_trader.research.feature_pipeline import FeaturePipeline
from reinforce_trader.research.models.kmeans_model_trainer import KmeansModelTrainer


def normalize_sequences(input_sequences: np.ndarray):
    # Extract the first timestep across all sequences for normalization
    first_timesteps = input_sequences[:, 0, 0]
    
    # Perform the log transformation and normalization in a vectorized manner
    transformed_sequences = np.log(input_sequences[:, :, 0]) - np.log(first_timesteps)[:, None]
    
    # Reshape the output to add the third dimension back
    return transformed_sequences[..., np.newaxis]


def create_clustering_v1(hparams):
    # datalake_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
    dl_client = DatalakeClient()

    # initialize pipelines
    feature_pipeline = FeaturePipeline(
        pipeline=[
            lambda array: array[:, :, [3]], # use only the close price
            normalize_sequences,
            lambda array: array.reshape(array.shape[0], -1),  # flatten the last 2 dimensions (seq * channel)
            # lambda array: array[:, :, 0].reshape(array.shape[0], -1),  # flatten the last 2 dimensions (seq * channel)
        ],
        params={}
    )

    
    trainer = KmeansModelTrainer(
        hparams=hparams,
        dl_client=dl_client,
        feature_pipeline=feature_pipeline,
    )
    return trainer
