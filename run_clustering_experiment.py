import matplotlib.pyplot as plt

from reinforce_trader.research.datalake_client import DatalakeClient
from reinforce_trader.research.feature_pipeline import FeaturePipeline
from reinforce_trader.research.dataset import Dataset
from reinforce_trader.research.models.sklearn_model_trainer import SklearnModelTrainer
from reinforce_trader.research.features.dct_feature import get_dct, get_dct_reconstruction
from reinforce_trader.research.features.standardizing_feature import get_minmax_scaling
from reinforce_trader.research.visualizations import plot_clustered_sequences_with_plotly, plot_elbow_and_silhouette


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
    # model_ckpt_dir = './model_ckpts/kmeans-20'
    # k = hparams['model']['n_clusters']
    # create the dataset
    dl_client = DatalakeClient()
    df = dl_client.get_table(
        data_source='yfinance',
        ticker='GOOGL',
        columns=['close'],
        start_date='2013-01-01',
        end_date='2018-12-31'
    )
    dataset = Dataset(df).create_partitions(
        test_size=0.1,
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
    model = trainer.train(dataset, feature_pipeline)

    # trainer.save(model_ckpt_dir='./model_ckpts/kmeans-28')

    # visualize the sequences
    sequences = dataset.get_partition(
        'train',
        'feature',
        transformation=lambda array: feature_pipeline.run(array)[0],  # TODO: this is ungly
    )
    labels = model.predict(sequences)
    # Get centroids
    centroids = model.cluster_centers_
    plot_clustered_sequences_with_plotly(hparams['model']['n_clusters'], labels, sequences, centroids)

    
if __name__ == '__main__':
    main()
