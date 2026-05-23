import os
import re

from src.exceptions import FileReadError

MAX_FILE_SIZE = 5 * 1024 * 1024
PATH_PATTERN = '@::(.+?)::'


def read_file(path: str) -> str:
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError as error:
        raise FileReadError(f'Error: file {path} is not valid utf-8 text') from error
    except OSError as error:
        raise FileReadError(f'Error: cannot read file {path}') from error


def read_file_size_restriction(path: str) -> str:
    if not os.path.exists(path):
        raise FileReadError(f'Error: file {path} not found')
    
    if os.path.getsize(path) > MAX_FILE_SIZE:
        raise FileReadError(f'Error: file {path} is too big')

    return read_file(path)


def read_file_no_restrictions(path: str) -> str:
    if not os.path.exists(path):
        raise FileReadError(f'Error: file {path} not found')

    return read_file(path)
    

def inline_files(text: str) -> str:
    paths = re.findall(PATH_PATTERN, text)

    for match in paths:
        content = read_file_size_restriction(match)
        text = text.replace(f'@::{match}::', f'\n{content}\n')

    return text
