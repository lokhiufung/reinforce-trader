
from reinforce_trader.research.feature_pipeline import FeaturePipeline
from reinforce_trader.research.datalake_client import DatalakeClient
from reinforce_trader.research.sampler.sampler import Sampler
from reinforce_trader.research.models.base_model_traniner import BaseModelTrainer

class SupervisedModelTrainer(BaseModelTrainer):
    def __init__(
            self,
            hparams: dict,
            dl_client: DatalakeClient,
            feature_pipeline: FeaturePipeline,
            label_pipeline: FeaturePipeline,
            sampler: Sampler=None,
        ):
        super().__init__(self, hparams, dl_client, feature_pipeline, sampler)
        # REMINDER: there should be a pipeline to construct label
        self.label_pipeline = label_pipeline

    