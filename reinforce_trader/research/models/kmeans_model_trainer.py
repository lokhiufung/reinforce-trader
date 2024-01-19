from typing import Dict
from numpy import ndarray

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score

from reinforce_trader.research.models.unsupervised_model_trainer import UnsupervisedModelTrainer
from reinforce_trader.research.get_sequences import get_rolling_window_sequences
from reinforce_trader.research.data_splitters.gapped_data_splitter import gapped_data_splitter


class KmeansModelTrainer(UnsupervisedModelTrainer):
    def __init__(
            self,
            hparams,
            dl_client,
            feature_pipeline,
            sampler=None,
        ):
        super().__init__(
            hparams,
            dl_client,
            feature_pipeline,
            sampler,
        )
        self.window_size = self.hparams['data']['window_size']

    def _get_datasets(self) -> Dict[str, Dict[str, ndarray]]:
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
            x = dataset_array
            x, x_analysises = self.feature_pipeline.run(x)
            
            datasets[dataset_name]['feature'] = x
            datasets[dataset_name]['label'] = x  # label == input in unsupervised learning
            # datasets[dataset_name]['feature'] = np.zeros_like(x)  # TEMP: this is useful for testing. The model should act as random guessing
            # datasets[dataset_name]['label'] = y

            self.analysises[dataset_name] = {}
            self.analysises[dataset_name]['feature'] = x_analysises

        return datasets

    def _train_step(self, x, y):
        clf = KMeans(**self.hparams['model'])
        clf.fit(x)
        return clf

    def _test_step(self, x, y):
        # Assign clusters to x
        y_pred = self.model.predict(x)
        
        # Since KMeans is unsupervised, we don't have true y labels, 
        # and y is actually the input x itself. We can use x to calculate the silhouette score.
        
        # Silhouette Score
        try:
            silhouette = silhouette_score(x, y_pred)
        except ValueError:  # If there is only one cluster, silhouette score cannot be calculated
            silhouette = None

        # Davies-Bouldin Index
        try:
            davies_bouldin = davies_bouldin_score(x, y_pred)
        except ValueError:  # If all points are in one cluster, returns error
            davies_bouldin = None
        
        # Return the evaluation metrics in a dictionary
        return {
            'silhouette_score': silhouette,
            'davies_bouldin_score': davies_bouldin
        }