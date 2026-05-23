from src.file_attachment import read_file_no_restrictions
from src.exceptions import ChunksError


DEFAULT_SPLIT_VALUE = 1
ASK_FILE_PATH = 'Введите путь до файла'
ASK_CHUNK_PROMPT = 'Принято. Что нужно сделать для каждого фрагмента?'
START_OUTPUT = 'Принято. Начинаю обработку:'
END_OUTPUT = 'Обработка файла завершена'


def ask_file_path() -> str:
    print(ASK_FILE_PATH)
    path = input('>>> ').strip()

    return path


def ask_chunk_prompt() -> str:
    print(ASK_CHUNK_PROMPT)
    prompt = input('>>> ').strip()

    return prompt


def print_start_processing() -> None:
    print(START_OUTPUT)


def print_finish_processing() -> None:
    print(END_OUTPUT)


def split_by_len(text: str, value: int) -> list[str]:
    if value <= 0:
        raise ChunksError('Error: len value must be positive')

    chunks: list[str] = []

    for i in range(0, len(text), value):
        chunks.append(text[i:(i + value)])

    return chunks


def split_by_paragraph(text: str, value: int = DEFAULT_SPLIT_VALUE) -> list[str]:
    if value <= 0:
        raise ChunksError('Error: paragraph value must be positive')

    chunks: list[str] = []

    paragraphs = [par for par in text.split('\n') if par.strip()]
    for i in range(0, len(paragraphs), value):
        chunks.append('\n'.join(paragraphs[i:(i + value)]))
    
    return chunks


def make_chunks(text: str, mode: str | None, value: int | None) -> list[str]:    
    if mode is None:
        if value is None:
            return split_by_paragraph(text)
        raise ChunksError('Error: mode is not given')
    
    if value is None:
        raise ChunksError('Error: mode value is not given')

    if mode == 'paragraph':
        return split_by_paragraph(text, value)
    
    if mode == 'len':
        return split_by_len(text, value)
    
    raise ChunksError(f'Error: unknown mode is given: {mode}')


def file_chunks(
    mode: str | None = None,
    value: int | None = None,
    path: str | None = None
) -> list[str]:

    if path is None:
        path = ask_file_path()

    text = read_file_no_restrictions(path)

    if not text:
        return []

    return make_chunks(text, mode, value)
