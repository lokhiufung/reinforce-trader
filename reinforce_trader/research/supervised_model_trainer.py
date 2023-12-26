from abc import ABC, abstractmethod


class SupervisedModelTrainer(ABC):
    def __init__(
            self,
            hparams,
            dl_client,
            feature_pipeline,
            label_pipeline
        ):
        self.hparams = hparams
        self.dl_client = dl_client
        self.feature_pipeline = feature_pipeline
        self.label_pipeline = label_pipeline
        self.datasets = {}

    def get_data(self, key):
        if key not in self.datasets:
            self.datasets = self._get_data()
        return self.datasets[key]
    
    @abstractmethod
    def _get_data(self):
        """define your data pipeline workflow here"""

    def train(self, generate_report=True):
        data = self.get_data('train')
        x_train, y_train = data['feature'], data['label']
        model = self._train_step(x_train, y_train)
        report = {}
        if generate_report:
            test_data = self.get_data('test')
            x_test, y_test = test_data['feature'], test_data['label']
            report['train'] = self._test_step(model, x_train, y_train)
            report['test'] = self._test_step(model, x_test, y_test)
            # evaluation_report
        return model, report

    # def test(self, report=True):
    #     x_train, y_train = self.get_data('train')
    #     model = self._train_step(x_train, y_train)
    #     report = {}
    #     if report:
    #         x_test, y_test = self.get_data('test')
    #         report['train'] = self._test_step(x_train, y_train)
    #         report['test'] = self._test_step(x_test, y_test)
    #         # evaluation_report
    #     return model, report
    
    @abstractmethod
    def _train_step(self, x, y):
        """a step to train"""

    @abstractmethod
    def _test_step(self, clf, x, y):
        """a step to test"""