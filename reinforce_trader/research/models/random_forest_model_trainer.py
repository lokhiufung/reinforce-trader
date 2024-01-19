import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score, f1_score

from reinforce_trader.research.models.supervised_model_trainer import SupervisedModelTrainer
from reinforce_trader.research.get_sequences import get_rolling_window_sequences
from reinforce_trader.research.data_splitters.gapped_data_splitter import gapped_data_splitter


class RandomForesModelTrainer(SupervisedModelTrainer):
    def __init__(
            self,
            hparams,
            dl_client,
            feature_pipeline,
            label_pipeline,
            sampler=None,
        ):
        super().__init__(
            hparams,
            dl_client,
            feature_pipeline,
            label_pipeline,
            sampler,
        )
        self.window_size = self.hparams['data']['feature_window_size'] + self.hparams['data']['label_window_size']

    @property
    def description(self):
        description = f"""
This model trainer is a random forest model trainer. It is a random forest classifier.

The trainer uses accuracy, F1 score and AUC of ROC as the metrics for model evaluation.
"""
        return description
    
    def _get_datasets(self):
        # load a table
        dfs = self.dl_client.get_tables(data_source='yfinance', tickers=self.hparams['data']['tickers'])
        df = dfs['GOOGL']  # TEMP: hard-coded for the moment
        # get the columns
        df = df[['open', 'high', 'low', 'close']]
        # turn df to array
        array = get_rolling_window_sequences(df, window_size=self.window_size)
        # train-test split
        array_splitted = gapped_data_splitter(array, test_size=self.hparams['data_splitter']['test_size'], gap_size=self.hparams['data_splitter']['gap_size'])
        datasets = {}
        for dataset_name, dataset_array in array_splitted.items():
            datasets[dataset_name] = {}

            # split sequences into feature and target
            x = dataset_array[:, :self.hparams['data']['feature_window_size'], :]
            y = dataset_array[:, self.hparams['data']['feature_window_size']:, :]
            x, x_analysises = self.feature_pipeline.run(x)
            y, y_analysises = self.label_pipeline.run(y)
            
            datasets[dataset_name]['feature'] = x
            datasets[dataset_name]['label'] = y
            # datasets[dataset_name]['feature'] = np.zeros_like(x)  # TEMP: this is useful for testing. The model should act as random guessing
            # datasets[dataset_name]['label'] = y

            self.analysises[dataset_name] = {}
            self.analysises[dataset_name]['feature'] = x_analysises
            self.analysises[dataset_name]['label'] = y_analysises

        return datasets
    
    def _train_step(self, x, y):
        clf = RandomForestClassifier(**self.hparams['model'])
        clf.fit(x, y)
        return clf

    def _test_step(self, x, y):
        y_pred = self.model.predict(x)
        y_pred_prob = self.model.predict_proba(x)  # Probabilities for ROC AUC
        # Evaluate the model
        accuracy = accuracy_score(y, y_pred)
        f1 = f1_score(y, y_pred, average='weighted')  # F1 Score
        # Compute ROC AUC Score
        if len(np.unique(y)) == 2:  # Binary classification
            y_pred_prob = self.model.predict_proba(x)[:, 1]  # Probabilities for ROC AUC # REMINDER: need reduce the dim first otherwise error
            roc_auc = roc_auc_score(y, y_pred_prob)  # Use probabilities for the positive class
        else:  # Multi-class classification
            roc_auc = roc_auc_score(y, y_pred_prob, multi_class='ovr')  # One-vs-Rest approach
        # report = classification_report(y, y_pred)
        return {
            'accuracy': accuracy,
            'f1': f1,
            'roc_auc': roc_auc
            # **report
        }
        
