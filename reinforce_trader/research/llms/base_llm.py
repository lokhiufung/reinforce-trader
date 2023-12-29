import time
from abc import ABC, abstractmethod

from auto_coder.sdk.core.errors import LLMMaxRetryError


class BaseLLM(ABC):
    def __init__(self, llm_config, max_api_call_retries=3, initial_wait=1.0, max_wait=16.0):
        self.max_api_call_retries = max_api_call_retries
        self.llm_config = llm_config
        self.initial_wait = initial_wait
        self.max_wait = max_wait

    def _request(self, params):
        # reminder: fung: will there be some cases that we dont need to reqest anything?
        raise NotImplementedError
    
    def _try_request(self, params, api_calls_retried=0, wait_time=None):
        if wait_time is None:
            wait_time = self.initial_wait

        try:
            # Assume this method makes the actual API call and returns the response
            return self._request(params)
        except Exception as err:
            if api_calls_retried < self.max_api_call_retries:
                time.sleep(wait_time)
                next_wait_time = min(wait_time * 2, self.max_wait)
                print(f"Error calling OpenAI. {err}\nRetrying {api_calls_retried + 1} of {self.max_api_call_retries} after {wait_time} seconds...")
                return self._try_request(params, api_calls_retried + 1, next_wait_time)
            else:
                raise LLMMaxRetryError(calls_retried=api_calls_retried)
    
    @abstractmethod
    def run(self):
        return
