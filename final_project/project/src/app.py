import re
import os

from src.config import Config
from src.client import LLMClient
from src.context_manager import ContextManager, CONTENT_KEY, ROLE_KEY
from src.exceptions import AIAssistantError
from src.file_attachment import inline_files
from src.file_chunks import (
    file_chunks,
    ask_chunk_prompt,
    print_start_processing,
    print_finish_processing
)


EXIT_COMMAND = r'\q'
RESET_COMMAND = '/reset'
CHUNK_COMMAND_PATTERN = (
    r'^/(file_chunk|filechunk)'
    r'(\s+(paragraph|len)=\d+)?'
    r'(\s+-y)?'
    r'(\s+(?!(paragraph|len)=)\S+)?'
    r'$'
)
LEN_OF_PARAM_PARAGRAPH = 10
LEN_OF_PARAM_LEN = 4

USER_ROLE = 'user'
AI_ROLE = 'assistant'


def is_file_chunk_command(command: str) -> bool:
    return re.fullmatch(CHUNK_COMMAND_PATTERN, command) is not None


def clear_screen() -> None:
    clear_value = 'cls' if os.name == 'nt' else 'clear'
    os.system(clear_value)


def handle_reset(context: ContextManager) -> None:
    context.reset()
    clear_screen()


def parse_chunk_parameters(command: str) -> tuple[str | None, int | None, str | None, bool]:
    parameters = command.split()
    
    mode: str | None = None
    value: int | None = None
    path: str | None = None
    auto: bool = False

    for param in parameters[1:]:
        if 'paragraph' in param:
            mode = 'paragraph'
            value = int(param[LEN_OF_PARAM_PARAGRAPH:])

        elif 'len' in param:
            mode = 'len'
            value = int(param[LEN_OF_PARAM_LEN:])

        elif param == '-y':
            auto = True

        else:
            path = param

    return mode, value, path, auto


def handle_file_chunks(
    client: LLMClient,
    mode: str | None,
    value: int | None,
    path: str | None,
    auto: bool
) -> None:
    
    chunks = file_chunks(mode, value, path)

    prompt = ask_chunk_prompt()

    print_start_processing()

    for chunk in chunks:
        message = [
            {
                ROLE_KEY: USER_ROLE,
                CONTENT_KEY: f'{prompt}\n\n{chunk}'
            }
        ]

        try:
            client.ask_stream(message)
        except KeyboardInterrupt:
            print()
            return

        if not auto:
            command = input('>>> ')

            if command == EXIT_COMMAND:
                return

    print_finish_processing()


def handle_ask(command: str, client: LLMClient, context: ContextManager) -> None:
    if not command:
        return
    
    command = inline_files(command)

    context.add_message(USER_ROLE, command)

    try:
        response = client.ask_stream(context.get_messages())
    except KeyboardInterrupt:
        context.delete_last()
        print()
        return
    
    context.add_message(AI_ROLE, response)


def parse_command(command: str, client: LLMClient, context: ContextManager) -> None:
    try:
        if command == RESET_COMMAND:
            handle_reset(context)
            return

        if is_file_chunk_command(command):
            mode, value, path, auto = parse_chunk_parameters(command)
            handle_file_chunks(client, mode, value, path, auto)
            return

        handle_ask(command, client, context)

    except AIAssistantError as error:
        print(error)


def run(cnf: Config) -> None:
    client = LLMClient(cnf)
    context = ContextManager(cnf)

    while True:
        try:
            user_prompt = input('>>> ').strip()
        except EOFError:
            print()
            break

        if user_prompt == EXIT_COMMAND:
            break

        parse_command(user_prompt, client, context)
