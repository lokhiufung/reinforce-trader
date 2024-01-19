from reinforce_trader.backtesting.signallers.base_signaller import BaseSignaller


class ClusterSignaller(BaseSignaller):
    def __init__(self, window_size, trainer, feature_pipeline, buy_cluster, sell_cluster=None):
        super().__init__(window_size=window_size)
        self.trainer = trainer
        self.feature_pipeline = feature_pipeline
        self.buy_cluster = buy_cluster
        self.sell_cluster = sell_cluster
        
    def get_signals(self, sequences):
        features, _ = self.feature_pipeline.run(sequences)
        predicted_clusters = self.trainer.model.predict(features)
        signals = []
        for predicted_cluster in predicted_clusters: 
            if predicted_cluster == self.buy_cluster:
                signals.append(1)
            elif self.sell_cluster is not None and predicted_cluster == self.sell_cluster:
                signals.append(-1)
            else:
                signals.append(0)
        return signals
