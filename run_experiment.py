from datetime import datetime

from reinforce_trader.research.create_classifier_v1 import create_classifier_v1
from reinforce_trader.research.agents.report_analyst_agent import ReportAnalystAgent


HPARAMS = {
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

def main():
    trainer = create_classifier_v1(hparams=HPARAMS)
    model, report = trainer.train(to_analyst=True)


    report_analyst_agent = ReportAnalystAgent.from_llm_config(
        llm_config={
            'max_tokens': 6000,
            'temperature': 0.3,
            'model': 'gpt-4'
        }
    )
    # Generate the report
    analyst_report = report_analyst_agent.act(report=report)

    # Get the current date in your preferred format
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Create a filename with the current date
    filename = f'./analyst_reports/analyst_report_{current_date}.txt'

    # Write the report to a file with the date in its name
    with open(filename, 'w') as f:
        f.write(analyst_report)


if __name__ == '__main__':
    main()
    