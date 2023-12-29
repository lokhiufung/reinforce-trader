from reinforce_trader.research.agents.llm_agent import LLMAgent


USER_PROMPT_TEMPLATE = """
""" 

SYSTEM_PROMPT_TEMPLATE = """
"""


class ReportAnalystAgent(LLMAgent):
    
    NAME = 'report_analyst_agent'
    USER_PROMPT_TEMPLATE = USER_PROMPT_TEMPLATE

    def get_messages(self, report: dict):
        return [
            {'role': 'user', 'content': ''},
        ]
    

    def get_action(self, generated_text) -> list[str]:
        return self.parse_json(generated_text)
