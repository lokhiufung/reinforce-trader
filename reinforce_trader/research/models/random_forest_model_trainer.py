import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score, f1_score

from reinforce_trader.research.supervised_model_trainer import SupervisedModelTrainer
from reinforce_trader.research.get_sequences import get_rolling_window_sequences
from reinforce_trader.research.data_splitters.gapped_data_splitter import gapped_data_splitter


class RandomForesModelTrainer(SupervisedModelTrainer):
    def __init__(
            self,
            hparams,
            dl_client,
            feature_pipeline,
            label_pipeline
        ):
        super().__init__(
            hparams,
            dl_client,
            feature_pipeline,
            label_pipeline
        )
        self.window_size = self.hparams['feature_window_size'] + self.hparams['label_window_size']

    def _get_data(self):
        # load a table
        df = self.dl_client.get_table(data_src='yfinance', ticker=self.hparams['ticker'])
        # get the columns
        df = df[['Open', 'High', 'Low', 'Close']]
        # turn df to array
        array = get_rolling_window_sequences(df, window_size=self.window_size)
        # train-test split
        array_splitted = gapped_data_splitter(array, test_size=self.hparams['test_size'], gap_size=self.hparams['gap_size'])
        datasets = {}
        for dataset_name, dataset_array in array_splitted.items():
            datasets[dataset_name] = {}

            # split sequences into feature and target
            x = dataset_array[:, :self.hparams['feature_window_size'], :]
            y = dataset_array[:, self.hparams['feature_window_size']:, :]
            x, x_analysises = self.feature_pipeline.run(x)
            y, y_analysises = self.label_pipeline.run(y)
            
            datasets[dataset_name]['feature'] = x
            datasets[dataset_name]['label'] = y

            self.analysises[dataset_name] = {}
            self.analysises[dataset_name]['feature'] = x_analysises
            self.analysises[dataset_name]['label'] = y_analysises

        return datasets
    
    def _train_step(self, x, y):
        clf = RandomForestClassifier(random_state=self.hparams['seed'])
        clf.fit(x, y)
        return clf

    def _test_step(self, clf, x, y):
        y_pred = clf.predict(x)
        y_pred_prob = clf.predict_proba(x)  # Probabilities for ROC AUC
        # Evaluate the model
        accuracy = accuracy_score(y, y_pred)
        f1 = f1_score(y, y_pred, average='weighted')  # F1 Score
        # Compute ROC AUC Score
        if len(np.unique(y)) == 2:  # Binary classification
            y_pred_prob = clf.predict_proba(x)[:, 1]  # Probabilities for ROC AUC # REMINDER: need reduce the dim first otherwise error
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
        
