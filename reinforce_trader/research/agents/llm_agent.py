from abc import abstractmethod

from reinforce_trader.research.agents.base_agent import BaseAgent


class LLMAgent(BaseAgent):
    def __init__(self, llm, debug=True, max_agent_act_retries=1, version="stable"):
        super().__init__(debug, version)
        self.max_agent_act_retries = max_agent_act_retries
        self.llm = llm

    def _act(self, **kwargs):
        # get messages
        messages = self.get_messages(**kwargs)
        # call llm
        if self.debug:
            self.print_user_message('kwargs', kwargs)
            self.print_user_message('messages', messages)
            self.logger.debug(f"agent={self.name} | {kwargs=} | {messages=}")
        llm_output = self.llm.run(
            messages=messages
        )
        if self.debug:
            self.print_agent_message(self.name, str(llm_output))
            self.logger.debug(f'agent={self.name} | {llm_output=}')
        agent_action = self.get_action(llm_output)
        return agent_action
    
    @abstractmethod
    def get_messages(self, **kwargs):
        """"""

    @abstractmethod
    def get_action(self, generated_text):
        """"""
    
    @classmethod
    def from_llm_config(cls, llm_config, llm_backend='openai', max_api_call_retries=3, max_agent_act_retries=1, debug=True, *args, **kwargs):
        if llm_backend == 'openai':
            from auto_coder.sdk.core.llms.openai_llm import OpenaiLLM

            llm = OpenaiLLM(llm_config, max_api_call_retries, debug=debug)
        else:
            raise ValueError(f'{llm_backend} is not supported now')
        
        # build an agent
        agent = cls(llm=llm, max_agent_act_retries=max_agent_act_retries, debug=debug, *args, **kwargs)
        return agent
    