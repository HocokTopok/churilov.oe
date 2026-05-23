from typing import cast
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from src.config import Config
from src.exceptions import LLMClientError

class LLMClient:
    def __init__(self, cnf: Config):
        self.client = OpenAI(
            base_url=cnf.api_host,
            api_key=cnf.api_key
        )
        self.model = cnf.model
        self.temperature = cnf.temperature


    def ask(self, messages: list[dict[str, str]]) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=cast(list[ChatCompletionMessageParam], messages),
                temperature=self.temperature
            )
        except Exception as error:
            raise LLMClientError('Error: model request failed') from error
        
        answer = response.choices[0].message.content

        if answer is None:
            return ''
        
        print(answer)
        return answer
    
    def ask_stream(self, messages: list[dict[str, str]]) -> str:
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=cast(list[ChatCompletionMessageParam], messages),
                temperature=self.temperature,
                stream=True
            )
        except Exception as error:
            raise LLMClientError('Error: model stream request failed') from error
        
        answer = ''

        try:
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta is not None:
                    print(delta, end='', flush=True)
                    answer += delta
            print()
            return answer
        except Exception as error:
            raise LLMClientError('Error: model stream reading failed') from error
