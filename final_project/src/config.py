import yaml
import os
from dataclasses import dataclass
from typing import Any
from src.exceptions import ConfigError


API_KEY = 'API_KEY'
API_HOST = 'API_HOST'
MODEL = 'MODEL'
TEMPERATURE = 'TEMPERATURE'
LIMIT_CHARS = 'LIMIT_CHARS'
LIMIT_MESSAGES = 'LIMIT_MESSAGES'

DEFAULT_TEMPERATURE_VALUE = 0.3
DEFAULT_LIMIT_CHARS_VALUE = 10000
DEFAULT_LIMIT_MESSAGES_VALUE = 20


@dataclass
class Config:
    api_host: str
    api_key: str
    model: str
    temperature: float
    limit_messages: int | None
    limit_chars: int | None
    system_prompt: str | None
    

def get_parameter(
    data: dict[str, Any],
    env_name: str,
    yaml_name: str,
    cast: type = str,
    default: Any = None
) -> Any:
    
    value: Any = os.environ.get(env_name, data.get(yaml_name, default))

    if value is None:
        raise ConfigError(f'Error: parameter {yaml_name} is not given')
    
    try:
        return cast(value)
    except (ValueError, TypeError) as error:
        raise ConfigError(f'Error: wrong value for parameter {yaml_name}') from error


def get_system_prompt(data: dict[str, Any], yaml_name: str = 'system_prompt') -> str | None:
    value: Any = data.get(yaml_name)

    return value if value is None else str(value)


def check_config(cnf: Config) -> None:
    if not cnf.api_host:
        raise ConfigError('Error: parameter api_host is empty')
    if not cnf.api_key:
        raise ConfigError('Error: parameter api_key is empty')
    if not cnf.model:
        raise ConfigError('Error: parameter model is empty')
    if cnf.temperature < 0 or cnf.temperature > 1:
        raise ConfigError('Error: parameter temperature must be between 0 and 1')
    if not cnf.api_host.startswith(('http://', 'https://')):
        raise ConfigError('Error: parameter api_host must start with http:// or https://')
    

def load_config(path: str = 'config.yaml') -> Config:
    file_values: dict[str, Any] = {}

    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                file_values = yaml.safe_load(file) or {}
        except UnicodeDecodeError as error:
            raise ConfigError(f'Error: file {path} is not valid utf-8 text') from error
        except OSError as error:
            raise ConfigError(f'Error: cannot read file {path}') from error

    config: Config = Config(
        api_host=get_parameter(file_values, API_HOST, 'api_host'),
        api_key=get_parameter(file_values, API_KEY, 'api_key'),
        model=get_parameter(file_values, MODEL, 'model'),
        temperature=get_parameter(file_values, TEMPERATURE,
                                  'temperature', float, DEFAULT_TEMPERATURE_VALUE),
        limit_chars=get_parameter(file_values, LIMIT_CHARS,
                                  'limit_chars', int, DEFAULT_LIMIT_CHARS_VALUE),
        limit_messages=get_parameter(file_values, LIMIT_MESSAGES,
                                     'limit_messages', int, DEFAULT_LIMIT_MESSAGES_VALUE),
        system_prompt=get_system_prompt(file_values)
    )

    check_config(config)

    return config
