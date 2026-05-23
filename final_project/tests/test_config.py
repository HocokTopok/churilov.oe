import pytest
from typing import Any
from pathlib import Path
from pytest import MonkeyPatch

from src.config import Config, get_parameter, get_system_prompt, check_config, load_config
from src.exceptions import ConfigError


def test_pos_get_parameter_env_and_yaml(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv('API_KEY', 'from_env')
    data = {'api_key': 'from_yaml'}

    result = get_parameter(data, 'API_KEY', 'api_key')

    assert result == 'from_env'


def test_pos_get_parameter_only_yaml(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.delenv('API_KEY', raising=False)
    data = {'api_key': 'from_yaml'}

    result = get_parameter(data, 'API_KEY', 'api_key')

    assert result == 'from_yaml'


def test_neg_get_parameter_missing_parameter(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.delenv('API_KEY', raising=False)
    data: dict[str, Any] = {}

    with pytest.raises(ConfigError, match='api_key'):
        get_parameter(data, 'API_KEY', 'api_key')


def test_neg_get_parameter_wrong_value(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv('TEMPERATURE', 'Wolf')
    data: dict[str, Any] = {}

    with pytest.raises(ConfigError, match='wrong value'):
        get_parameter(data, 'TEMPERATURE', 'temperature', float)


def test_pos_get_system_prompt() -> None:
    data = {'system_prompt': 'The wolf is not a lion, but a wolf'}

    result = get_system_prompt(data)

    assert result == 'The wolf is not a lion, but a wolf'


def test_pos_check_config() -> None:
    cnf = Config(
        api_host='http://localhost:11434/v1/',
        api_key='ollama',
        model='qwen2.5-coder:7b',
        temperature=1.0,
        limit_messages=20,
        limit_chars=10000,
        system_prompt=None
    )

    check_config(cnf)


def test_neg_check_config_wrong_api_host() -> None:
    cnf = Config(
        api_host='The wolf is not a lion, but a wolf',
        api_key='ollama',
        model='qwen2.5-coder:7b',
        temperature=1.0,
        limit_messages=20,
        limit_chars=10000,
        system_prompt=None
    )

    with pytest.raises(ConfigError, match='api_host'):
        check_config(cnf)


def test_neg_check_config_empty_parameter() -> None:
    cnf = Config(
        api_host='http://localhost:11434/v1/',
        api_key='ollama',
        model='',
        temperature=1.0,
        limit_messages=20,
        limit_chars=10000,
        system_prompt=None
    )

    with pytest.raises(ConfigError, match='empty'):
        check_config(cnf)


def test_neg_check_config_wrong_temperature() -> None:
    cnf = Config(
        api_host='http://localhost:11434/v1/',
        api_key='ollama',
        model='qwen2.5-coder:7b',
        temperature=2.0,
        limit_messages=20,
        limit_chars=10000,
        system_prompt=None
    )

    with pytest.raises(ConfigError, match='temperature'):
        check_config(cnf)


def test_pos_load_config(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv('API_HOST', raising=False)
    monkeypatch.delenv('API_KEY', raising=False)
    monkeypatch.delenv('MODEL', raising=False)
    monkeypatch.delenv('TEMPERATURE', raising=False)
    monkeypatch.delenv('LIMIT_CHARS', raising=False)
    monkeypatch.delenv('LIMIT_MESSAGES', raising=False)

    config_path = tmp_path / 'test.yaml'

    config_path.write_text(
        """
api_host: http://localhost:11434/v1/
api_key: ollama
model: qwen2.5-coder:7b
temperature: 0.3
limit_chars: 10000
limit_messages: 20
""",
        encoding='utf-8',
    )

    cnf = load_config(str(config_path))

    assert cnf.api_key == 'ollama'
    assert cnf.temperature == 0.3


def test_neg_load_config_missing_parameter(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv('API_HOST', raising=False)
    monkeypatch.delenv('API_KEY', raising=False)
    monkeypatch.delenv('MODEL', raising=False)
    monkeypatch.delenv('TEMPERATURE', raising=False)
    monkeypatch.delenv('LIMIT_CHARS', raising=False)
    monkeypatch.delenv('LIMIT_MESSAGES', raising=False)

    config_path = tmp_path / 'test.yaml'

    config_path.write_text(
        """
api_host: http://localhost:11434/v1/
model: qwen2.5-coder:7b
temperature: 0.3
limit_chars: 10000
limit_messages: 20
""",
        encoding='utf-8',
    )
    
    with pytest.raises(ConfigError, match='api_key'):
        load_config(str(config_path))
