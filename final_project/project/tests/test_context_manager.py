from src.config import Config
from src.context_manager import ContextManager


def test_pos_count_chars() -> None:
    cnf = Config(
        api_host='http://localhost:11434/v1/',
        api_key='ollama',
        model='qwen2.5-coder:7b',
        temperature=0.7,
        limit_messages=10,
        limit_chars=1000,
        system_prompt=None
    )

    context = ContextManager(cnf)
    context.add_message('user', 'abc')
    context.add_message('assistant', 'de')
    
    assert context.count_chars() == 5


def test_pos_add_message() -> None:
    cnf = Config(
        api_host='http://localhost:11434/v1/',
        api_key='ollama',
        model='qwen2.5-coder:7b',
        temperature=0.7,
        limit_messages=20,
        limit_chars=1000,
        system_prompt=None
    )

    mng = ContextManager(cnf)
    mng.add_message('user', 'The wolf is not a lion, but a wolf')

    assert mng.messages == [
        {'role': 'user', 'content': 'The wolf is not a lion, but a wolf'}
    ]


def test_pos_reset() -> None:
    cnf = Config(
        api_host='http://localhost:11434/v1/',
        api_key='ollama',
        model='qwen2.5-coder:7b',
        temperature=0.7,
        limit_messages=20,
        limit_chars=1000,
        system_prompt=None
    )

    mng = ContextManager(cnf)
    mng.add_message('user', 'The wolf is not a lion, but a wolf')
    mng.reset()

    assert mng.messages == []


def test_pos_limit_messages() -> None:
    cnf = Config(
        api_host='http://localhost:11434/v1/',
        api_key='ollama',
        model='qwen2.5-coder:7b',
        temperature=0.7,
        limit_messages=2,
        limit_chars=1000,
        system_prompt=None
    )

    mng = ContextManager(cnf)
    mng.add_message('user', 'Wolf')
    mng.add_message('assistant', 'Lion')
    mng.add_message('assistant', 'Fox')

    assert mng.messages == [
        {'role': 'assistant', 'content': 'Lion'},
        {'role': 'assistant', 'content': 'Fox'}
    ]


def test_pos_limit_chars() -> None:
    cnf = Config(
        api_host='http://localhost:11434/v1/',
        api_key='ollama',
        model='qwen2.5-coder:7b',
        temperature=0.7,
        limit_messages=10,
        limit_chars=10,
        system_prompt=None
    )

    context = ContextManager(cnf)
    context.add_message('user', '12345')
    context.add_message('assistant', '67890')
    context.add_message('user', 'abcde')

    assert context.messages == [
        {'role': 'assistant', 'content': '67890'},
        {'role': 'user', 'content': 'abcde'},
    ]


def test_pos_limit_chars_cuts_single_message() -> None:
    cnf = Config(
        api_host='http://localhost:11434/v1/',
        api_key='ollama',
        model='qwen2.5-coder:7b',
        temperature=0.7,
        limit_messages=10,
        limit_chars=5,
        system_prompt=None
    )

    context = ContextManager(cnf)
    context.add_message('user', '123456789')

    assert context.messages == [
        {'role': 'user', 'content': '56789'},
    ]
