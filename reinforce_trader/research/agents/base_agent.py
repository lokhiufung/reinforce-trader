from abc import ABC, abstractmethod

from reinforce_trader.research.mixins.color_print_mixin import ColorPrintMixin
from reinforce_trader.research.mixins.text_parser_mixin import TextParserMixin
from reinforce_trader.research.mixins.image_input_parser_mixin import ImageInputParserMixin
from reinforce_trader.research.errors import AgentMaxRetryError
from reinforce_trader.logger import get_logger


logger = get_logger('agent', logger_lv='debug')


class BaseAgent(ABC, ColorPrintMixin, TextParserMixin, ImageInputParserMixin):
    NAME = None

    def __init__(self, debug=True, max_agent_act_retries=1, version="stable"):
        self.name = self.NAME
        if not self.name:
            raise ValueError('Must provide a NAME when creating the agent class')
        self.max_agent_act_retries = max_agent_act_retries

        self.debug = debug  # TODO: fung: add a debug mode for color print in console
        self.version = version
        # logger_lv = 'debug' if self.debug else 'info'
        self.logger = logger

    def _try_act(self, agent_act_retried, **kwargs):
        try:
            return self._act(**kwargs)
        # except LLMMaxRetryError as err:
        #     # if there are problems when calling llm, raise an error immediately
        #     raise LLMMaxRetryError(calls_retried=err.calls_retried)  # tmp: fung: may not be a good practice to handle error again in the agent layer
        except Exception as err:
            if agent_act_retried < self.max_agent_act_retries:
                self.logger.error(f"agent={self.name} | Error when parsing agent output. {err}\nRetrying {agent_act_retried} of {self.max_agent_act_retries}...")
                return self._try_act(agent_act_retried=agent_act_retried+1, **kwargs)
            else:
                raise AgentMaxRetryError(err, agent_act_retried)

    @abstractmethod
    def _act(self, **kwargs):
        ...

    def act(self, **kwargs):
        return self._try_act(**kwargs, agent_act_retried=0)
