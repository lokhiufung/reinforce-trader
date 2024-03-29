class ResearchAgentError(Exception):
    """"""


class LLMMaxRetryError(ResearchAgentError):
    def __init__(self, calls_retried, llm_backend=None):
        self.calls_retried = calls_retried
        self.llm_backend = llm_backend
        self.message = f'Unsolvabled error when calling {self.llm_backend} llm after {self.calls_retried} times'
        super().__init__(self.message)


class AgentMaxRetryError(ResearchAgentError):
    def __init__(self, msg, agent_act_retried, agent_name=None):  # TODO: fung: add name if needed
        self.agent_act_retried = agent_act_retried
        self.agent_name = agent_name
        self.message = f'Unsolvabled error when parsing {self.agent_name} agent output after {agent_act_retried} times: {msg}'
        super().__init__(self.message)
