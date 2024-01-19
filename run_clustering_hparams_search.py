from tqdm import tqdm
from sklearn.metrics import silhouette_score, davies_bouldin_score

from reinforce_trader.research.datalake_client import DatalakeClient
from reinforce_trader.research.feature_pipeline import FeaturePipeline
from reinforce_trader.research.dataset import Dataset
from reinforce_trader.research.models.sklearn_model_trainer import SklearnModelTrainer
from reinforce_trader.research.features.dct_feature import get_dct, get_dct_reconstruction
from reinforce_trader.research.features.standardizing_feature import get_minmax_scaling
from reinforce_trader.research.visualizations import plot_elbow_and_silhouette


hparams = {
    'dataset': {
        'tickers': ['GOOGL'],
        'window_size': 56,
        'long_window_size': 28,
        'test_size': 0.1,
        'gap_size': 28,
    },
    'model': {
        'n_clusters': 5,  # REMINDER: 5 is optimal
        'init': 'k-means++',
        'n_init': 'auto',
        'max_iter': 300,
        'tol': 1e-4,
        'algorithm': 'lloyd',
        'random_state': 1
    }
}


def main():
    # create the dataset
    dl_client = DatalakeClient()
    df = dl_client.get_table(
        data_source='yfinance',
        ticker='GOOGL',
        columns=['close']
    )
    dataset = Dataset(df).create_partitions(
        test_size=hparams['dataset']['test_size'],
        window_size=hparams['dataset']['window_size'],
        gap_size=hparams['dataset']['gap_size'],
        feature_len=hparams['dataset']['long_window_size'],
    )

    # create the feature pipelines
    feature_pipeline = FeaturePipeline(
        pipeline=[
            lambda x: x[:, :, 0],
            get_minmax_scaling,
            get_dct,
            get_dct_reconstruction,
        ],
        params={}
    )

    # create the model
    trainer = SklearnModelTrainer(
        hparams=hparams['model'],
        model_name='kmeans',
    )
    
    sse = {}
    silhouette_scores = {}
    db_index = {}
    for n_clusters in tqdm(range(2, 30)):
        # train the model
        hparams['model']['n_clusters'] = n_clusters
        trainer = SklearnModelTrainer(
            hparams=hparams['model'],
            model_name='kmeans',
        )   
        model = trainer.train(dataset, feature_pipeline)
        sse[n_clusters] = model.inertia_  # Sum of squared distances of samples to their closest cluster center
        silhouette_scores[n_clusters] = silhouette_score(
            dataset.get_partition('train', 'feature', transformation=lambda array: feature_pipeline.run(array)[0]),
            model.labels_
        )
        db_index[n_clusters] = davies_bouldin_score(
            dataset.get_partition('train', 'feature', transformation=lambda array: feature_pipeline.run(array)[0]),
            model.labels_
        )

    plot_elbow_and_silhouette(sse, silhouette_scores, db_index)

    
if __name__ == '__main__':
    main()
