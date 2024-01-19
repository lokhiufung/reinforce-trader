from reinforce_trader.backtesting.backtesting import Backtesting
from reinforce_trader.backtesting.strategies.naive_cluster_strategy import NaiveClusterStrategy
from reinforce_trader.backtesting.signallers.cluster_signaller import ClusterSignaller
from reinforce_trader.research.models.sklearn_model_trainer import SklearnModelTrainer
from reinforce_trader.research.feature_pipeline import FeaturePipeline
from reinforce_trader.research.features.standardizing_feature import get_minmax_scaling
from reinforce_trader.research.features.dct_feature import get_dct, get_dct_reconstruction
from reinforce_trader.research.datalake_client import DatalakeClient


def main():
    start_date = '2021-01-01'
    end_date = '2023-12-31'
    window_size = 28

    trainer = SklearnModelTrainer.from_model_ckpt(
    model_name='kmeans',
    model_ckpt_dir='./model_ckpts/kmeans-28'
    )
    dl_client = DatalakeClient()
    df = dl_client.get_table('yfinance', 'NVDA', start_date=start_date, end_date=end_date)

    bt = Backtesting()
    bt.add_data(df)

    feature_pipeline = FeaturePipeline(
        pipeline=[
            lambda x: x[:, :, 3],  # 3 is the close price
            get_minmax_scaling,
            get_dct,
            get_dct_reconstruction,
        ],
        params={}
    )
    strategy = NaiveClusterStrategy(
        stop_loss=0.05,
        take_profit=1,
        initial_balance=100*1000,
        bet_size=1.0
    )
    signaller = ClusterSignaller(
        window_size=window_size,
        trainer=trainer,
        feature_pipeline=feature_pipeline,
        buy_cluster=2,
        sell_cluster=3,
    )

    bt.run(strategy, signaller, plot=True)


if __name__ == '__main__':
    main()

