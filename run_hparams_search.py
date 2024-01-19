import itertools

from reinforce_trader.research.create_classifier_v1 import create_classifier_v1


class HparamsFactory:
    def __init__(self, params):
        self.params = params
        for key in self.params:
            setattr(self, key, params[key])
        
    def get_params(self, part, **kwargs):
        params = self.params.copy()
        for key in kwargs:
            if key in params[part]:
                params[part][key] = kwargs[key]
        return params


def main():
    hparams = {
        'data': {
            'tickers': ['GOOGL'],
            'feature_window_size': 28,
            'label_window_size': 14,
        },
        'feature_pipeline': {
            # frac diff
            'd': 0.63,
            'threshold': 0.01,
        },
        'label_pipeline': {
            # triple barrier
            'r_stop': 0.02,
            'r_take': 0.04,
        },
        'data_splitter': {
            'test_size': 0.1,
            'gap_size': 14,
        },
        'model': {
            'n_estimators': 100,
            'max_depth': None,
            'min_samples_split': 2,
            'min_samples_leaf': 1,
            'min_weight_fraction_leaf': 0.0,
            'max_features': 'sqrt',
            'max_leaf_nodes': None,
            'min_impurity_decrease': 0.0,
            'bootstrap': True,
            'oob_score': False,
            'ccp_alpha': 0.0,
            'max_samples': None,
            'random_state': 0
        }
    }
    hparams_factory = HparamsFactory(hparams)
    # TEMP
    max_depths_list = [1, 2, 3, 5, 8, 13, 21]
    n_estimators_list = [1, 2, 5, 10, 20, 40, 80, 100]

    combinations = itertools.product(max_depths_list, n_estimators_list)
    for max_depth, n_estimators in combinations:
        hparams = hparams_factory.get_params(
            part='model',
            max_depth=max_depth,
            n_estimators=n_estimators,
        )

        trainer = create_classifier_v1(hparams)

        model, report = trainer.train(to_analyst=False)
        print('(max_depth, n_estimators)={} | analysis={}'.format((max_depth, n_estimators), report['model_analysises']))
        

if __name__ == '__main__':
    main()