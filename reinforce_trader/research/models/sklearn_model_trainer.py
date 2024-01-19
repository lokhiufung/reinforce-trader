# TODO: this model trainer shoulds works for all sklearn models and disentagnle the data layer and feature layer from the model
import os
from importlib import import_module

from joblib import dump, load
import yaml

from reinforce_trader.research.dataset import Dataset


MODEL_FULL_NAMES = {
    'kmeans': 'sklearn.cluster.KMeans',
    'random_forest_classifer': 'sklearn.ensemble.RandomForestClassifer',
}


class SklearnModelTrainer:
    def __init__(self, hparams: dict, model_name: str, sklearn_model=None):
        self.hparams = hparams
        self.model_name = model_name
        self.model = sklearn_model
        if self.model is None:
            # import the model with the name
            model_full_name = MODEL_FULL_NAMES[self.model_name]
            sklearn_model_class_parent_name = '.'.join(model_full_name.split('.')[:-1])
            sklearn_model_class_name = model_full_name.split('.')[-1]
            self.model = getattr(import_module(sklearn_model_class_parent_name), sklearn_model_class_name)(**self.hparams)

    def train(
            self,
            dataset: Dataset,
            feature_pipeline,
            x_only=False,  # TODO: temperaory argument for unsupervised learning
        ):
        feature, _ = feature_pipeline.run(
            array=dataset.get_partition('train', 'feature')
        )
        if not x_only:
            target, _ = feature_pipeline.run(
                array=dataset.get_partition('train', 'target')
            )
            self.model.fit(feature, target)
        else:
            self.model.fit(feature)
        return self.model

    def test_cv(
            self,
            dataset: Dataset,
            feature_pipeline,
            x_only=False,
        ):
        for fold_index in range(dataset.num_folds):
            feature, _ = feature_pipeline.run(
                array=dataset.get_partition('test', 'feature', fold_index=fold_index)
            )
            if not x_only:
                target, _ = feature_pipeline.run(
                    array=dataset.get_partition('test', 'target')
                )
                predictions = self.model.predict(feature, target)
            else:
                predictions = self.model.predict(feature)
        # TODO
                
    def test(
            self,
            dataset: Dataset,
            feature_pipeline,
            x_only=False,
        ):
        feature = feature_pipeline.run(
            array=dataset.get_partition('test', 'feature')
        )
        if not x_only:
            target, _ = feature_pipeline.run(
                array=dataset.get_partition('test', 'target')
            )
            predictions = self.model.predict(feature, target)
        else:
            predictions = self.model.predict(feature)
        # TODO
            
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
        model_name: str,
        model_ckpt_dir: str,
    ):
        model_file_path = os.path.join(model_ckpt_dir, 'model.joblib')
        hparams_file_path = os.path.join(model_ckpt_dir, 'hparams.yaml')

        with open(hparams_file_path, 'r') as f:
            hparams = yaml.safe_load(f)
        
        sklearn_model = load(model_file_path)
        trainer = cls(
            hparams,
            model_name,
            sklearn_model=sklearn_model,
        )
        return trainer