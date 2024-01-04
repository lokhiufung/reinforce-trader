from reinforce_trader.research.agents.llm_agent import LLMAgent


USER_PROMPT_TEMPLATE = """
Here is the statistics gathered from the experiment:
{report_analysises}
""" 

SYSTEM_PROMPT_TEMPLATE = """
You are a senior data scientist. You are given a report of the statistics about an experiement of a model training pipeline.
There are 4 major components in the model training pipeline: 1) feature pipeline, 2) label pipeline, 3) sampler and 4) model training.

Here is the information about the feature pipeline:
####
{feature_pipeline_description}
####

Here is the information about the label pipeline:
####
{label_pipeline_description}
####

Here is the information about the model training:
####
{model_training_description}
####

Here is the information about the sampler:
####
{sampler_description}
####

Your job is to write a professional analysis about the experiement. You should focus on the following 3 objectives:
1. Describle the statistics of the feature pipeline (for each feature), label pipeline (for each feature), sampler and model training. You should always describe the results with the statistics provided.
2. Describle the observations you have about the report. You MUST support your observation with the provideded statistics.
3. Provide recommendations on improving the model training pipeline. Your recommendations provide a clear direction for me to explore in the next experiment. You MUST support your recommendation with the provideded statistics.

Here is an example of your analysis:
####
Feature Pipeline Statistics
1. FracDiffMultiChannelFeature
Description: This feature processes input data into fractionally differentiated series for each channel. It's designed for multidimensional data (samples, steps, channels).
Train Set Analysis:
Statistics per Channel:
Channel 0: Mean: 0.6129, Median: 0.6419, Max: 0.9674, Min: -0.2214, 75th percentile: 0.7056, 25th percentile: 0.5435.
...
Summary:
<Your descripiton of statistics here...>
Test Set Analysis:
Summary:
<Your descripiton of statistics here...>
2. TripleBarrierFeature
Description: Generates labels and actual returns based on open, high, low, and close prices in the input array.
Summary:
<Your descripiton of statistics here...>

Sampler Statistics
Summary:
<Your descripiton of statistics here...>

Model Training Analysis
Model Type: Supervised Random Forest Classifier.
Metrics Used: Accuracy, F1 score, ROC AUC.
Performance:
Summary:
<Your descripiton of statistics here...>


Observations:
1. <Your observation ...>
2. <Your observation ...>
...


Recommendations:
1. <Your recommendation ...>
2. <Your recommendation ...>
...

In summary, <your summary statement...>
####

Follow the structure of the example to write your analysis and return your analysis only.
"""


class ReportAnalystAgent(LLMAgent):
    
    NAME = 'report_analyst_agent'
    USER_PROMPT_TEMPLATE = USER_PROMPT_TEMPLATE

    def get_messages(self, report: dict):
        feature_pipeline_description = report['descriptions']['feature_pipeline']
        label_pipeline_description = report['descriptions']['label_pipeline']
        model_training_description = report['descriptions']['model']
        sampler_description = report['descriptions']['sampler']
        report_analysises = {
            'pipeline_analysises': report['pipeline_analysises'],
            'model_analysises': report['model_analysises'],
            'sampler_analysises': report['sampler_analysises']
        } 
        return [
            {'role': 'system', 'content': SYSTEM_PROMPT_TEMPLATE.format(
                feature_pipeline_description=feature_pipeline_description,
                label_pipeline_description=label_pipeline_description,
                model_training_description=model_training_description,
                sampler_description=sampler_description,
            )},
            {'role': 'user', 'content': USER_PROMPT_TEMPLATE.format(
                report_analysises=report_analysises
            )},
        ]

    def get_action(self, generated_text) -> list[str]:
        return generated_text
