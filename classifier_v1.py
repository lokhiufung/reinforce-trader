import os
from pprint import pprint

import numpy as np

from reinforce_trader.research.datalake_client import DatalakeClient
from reinforce_trader.research.feature_pipeline import FeaturePipeline
from reinforce_trader.research.features import FracDiffMultiChannelFeature, TripleBarrierFeature
from reinforce_trader.research.models.random_forest_model_trainer import RandomForesModelTrainer
from reinforce_trader.research.analyzers import DistAnalyzer, CorrAnalyzer, AutocorrAnalyzer 
from reinforce_trader.research.agents.report_analyst_agent import ReportAnalystAgent



def main():
    hparams = {
        'ticker': 'GOOGL',
        'test_size': 0.1,
        'gap_size': 14,
        'feature_window_size': 28,
        'label_window_size': 14,
        # frac diff
        'd': 0.63,
        'threshold': 0.01,
        # triple barrier
        'r_stop': 0.02,
        'r_take': 0.04,
        # model
        'seed': 0
    }    
    datalake_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
    template_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'datalake_template.yaml'))
    dl_client = DatalakeClient(datalake_dir=datalake_dir, template_file_path=template_file_path)

    # initialize pipelines
    feature_pipeline = FeaturePipeline(
        pipeline=[
            np.log,
            FracDiffMultiChannelFeature,
            lambda array: array.reshape(array.shape[0], -1),  # flatten the last 2 dimensions (seq * channel)
        ],
        params={
            'FracDiffMultiChannelFeature': {'d': hparams['d'], 'threshold': hparams['threshold']}
        },
        analyzers={
            'FracDiffMultiChannelFeature': [CorrAnalyzer()]
        }
    )

    label_pipeline = FeaturePipeline(
        pipeline=[
            TripleBarrierFeature,
            lambda array: array[:, 0],  # use the labels only 
        ],
        params={
            'TripleBarrierFeature': {'r_stop': hparams['r_stop'], 'r_take': hparams['r_take']}
        },
        analyzers={
            'TripleBarrierFeature': [DistAnalyzer()]  # TODO: only Feature can use analyzer
        }
    )

    trainer = RandomForesModelTrainer(
        hparams,
        dl_client,
        feature_pipeline=feature_pipeline,
        label_pipeline=label_pipeline,
    )

    model, report = trainer.train(to_analyst=True)
    
    report_analyst_agent = ReportAnalystAgent.from_llm_config(
        llm_config={
            'max_tokens': 6000,
            'temperature': 0.3,
            'model': 'gpt-3.5-turbo-16k'
        }
    )
    analyst_report = report_analyst_agent.act(report=report)

    with open('analyst_report.txt', 'w') as f:
        f.write(analyst_report)
    

if __name__ == '__main__':
    main()