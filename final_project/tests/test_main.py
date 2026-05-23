import pytest
from pytest import MonkeyPatch
from pytest import CaptureFixture
from typing import NoReturn

from src.config import Config
from src.exceptions import ConfigError
from src.main import main


def make_config() -> Config:
    return Config(
        api_host='http://localhost:11434/v1/',
        api_key='ollama',
        model='qwen2.5-coder:7b',
        temperature=1.0,
        limit_messages=20,
        limit_chars=10000,
        system_prompt=None,
    )


def test_pos_main(monkeypatch: MonkeyPatch) -> None:
    cnf = make_config()
    called = {'run': False}

    def fake_load_config() -> Config:
        return cnf

    def fake_run(config: Config) -> None:
        called['run'] = True
        assert config == cnf

    monkeypatch.setattr('src.main.load_config', fake_load_config)
    monkeypatch.setattr('src.main.run', fake_run)

    main()

    assert called['run']


def test_neg_main_application_error(
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str]
) -> None:
    
    def fake_load_config() -> NoReturn:
        raise ConfigError('Error: bad config')

    monkeypatch.setattr('src.main.load_config', fake_load_config)

    with pytest.raises(SystemExit) as error:
        main()

    captured = capsys.readouterr()

    assert error.value.code == 1
    assert captured.out == 'Error: bad config\n'


def test_neg_main_unknown_error(
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str]
) -> None:
    def fake_load_config() -> NoReturn:
        raise RuntimeError('babax')

    monkeypatch.setattr('src.main.load_config', fake_load_config)

    with pytest.raises(SystemExit) as error:
        main()

    captured = capsys.readouterr()

    assert error.value.code == 1
    assert 'CRITICAL ERROR: unexpected error: babax' in captured.out