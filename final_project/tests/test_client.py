import pytest
from pytest import MonkeyPatch
from typing import Any

from src.client import LLMClient
from src.config import Config
from src.exceptions import LLMClientError


def make_config() -> Config:
    return Config(
        api_host='http://localhost:11434/v1/',
        api_key='ollama',
        model='qwen2.5-coder:7b',
        temperature=1.0,
        limit_messages=20,
        limit_chars=10000,
        system_prompt=None
    )


class FakeMessage:
    content = 'The wolf is not a lion'


class FakeChoice:
    message = FakeMessage()


class FakeResponse:
    choices = [FakeChoice()]


def test_pos_client_init() -> None:
    cnf = make_config()

    LLMClient(cnf)


def test_pos_client_ask(monkeypatch: MonkeyPatch) -> None:
    cnf = make_config()

    client = LLMClient(cnf)

    def fake_create(**kwargs: Any) -> FakeResponse:
        return FakeResponse()
    
    monkeypatch.setattr(client.client.chat.completions, 'create', fake_create)

    result = client.ask([{'role': 'user', 'content': 'Auf'}])

    assert result == 'The wolf is not a lion'


def test_neg_client_ask(monkeypatch: MonkeyPatch) -> None:
    cnf = make_config()

    client = LLMClient(cnf)

    def fake_create(**kwargs: Any) -> FakeResponse:
        raise RuntimeError('api error')
    
    monkeypatch.setattr(client.client.chat.completions, 'create', fake_create)

    with pytest.raises(LLMClientError, match='model request failed'):
        client.ask([{'role': 'user', 'content': 'Auf'}])
