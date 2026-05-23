import pytest
from pathlib import Path

from src.file_attachment import MAX_FILE_SIZE, read_file_size_restriction, inline_files
from src.exceptions import FileReadError


def test_pos_read_file(tmp_path: Path) -> None:
    file_path = tmp_path / 'test.py'
    file_path.write_text(
        'The wolf is not a lion, but a wolf',
        encoding='utf-8'
    )

    result = read_file_size_restriction(str(file_path))

    assert result == 'The wolf is not a lion, but a wolf'


def test_neg_read_file_not_found(tmp_path: Path) -> None:
    file_path = tmp_path / 'missing.py'

    with pytest.raises(FileReadError, match='not found'):
        read_file_size_restriction(str(file_path))


def test_neg_read_file_big_size(tmp_path: Path) -> None:
    file_path = tmp_path / 'test.py'
    large_size = MAX_FILE_SIZE + 1
    file_path.write_text('Z' * large_size, encoding='utf-8')

    with pytest.raises(FileReadError, match='too big'):
        read_file_size_restriction(str(file_path))


def test_pos_inline_files(tmp_path: Path) -> None:
    first_file_path = tmp_path / 'first.py'
    second_file_path = tmp_path / 'second.cpp'
    first_file_path.write_text(
        'The wolf is not a lion, but a wolf',
        encoding='utf-8'
    )
    second_file_path.write_text(
        'The lion is a lion, but still not a wolf',
        encoding='utf-8'
    )

    text = f'#####@::{first_file_path}::#####@::{second_file_path}::#####'

    result = inline_files(text)

    expected = (
        '#####\n'
        'The wolf is not a lion, but a wolf\n'
        '#####\n'
        'The lion is a lion, but still not a wolf\n'
        '#####'
    )

    assert result == expected
