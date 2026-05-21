import pytest
from pathlib import Path

from src.file_chunks import file_chunks
from src.exceptions import ChunksError, FileReadError


def test_pos_file_chunks_default(tmp_path: Path) -> None:
    file_path = tmp_path / 'test.py'
    file_path.write_text('The wolf\nThe lion\nThe wolf', encoding='utf-8')

    result = file_chunks(path=str(file_path))

    assert result == ['The wolf', 'The lion', 'The wolf']


def test_pos_file_chunks_len(tmp_path: Path) -> None:
    file_path = tmp_path / 'test.py'
    file_path.write_text('123456789', encoding='utf-8')

    result = file_chunks(mode='len', value=3, path=str(file_path))

    assert result == ['123', '456', '789']


def test_pos_file_chunks_paragraph(tmp_path: Path) -> None:
    file_path = tmp_path / 'test.py'
    file_path.write_text(
        'The wolf\nThe lion\nThe wolf\nThe wolf\nThe lion\nThe wolf',
        encoding='utf-8'
    )

    result = file_chunks(mode='paragraph', value=3, path=str(file_path))

    assert result == [
        'The wolf\nThe lion\nThe wolf',
        'The wolf\nThe lion\nThe wolf'
    ]


def test_neg_file_chunks_unknown_mode(tmp_path: Path) -> None:
    file_path = tmp_path / 'test.py'
    file_path.write_text('The wolf', encoding='utf-8')

    with pytest.raises(ChunksError, match='unknown'):
        file_chunks(mode='goida', value=67, path=str(file_path))


def test_neg_file_chunks_no_value_but_mode(tmp_path: Path) -> None:
    file_path = tmp_path / 'test.py'
    file_path.write_text('The wolf', encoding='utf-8')

    with pytest.raises(ChunksError, match='not given'):
        file_chunks(mode='paragraph', path=str(file_path))


def test_neg_file_chunks_no_mode_but_value(tmp_path: Path) -> None:
    file_path = tmp_path / 'test.py'
    file_path.write_text('The wolf', encoding='utf-8')

    with pytest.raises(ChunksError, match='not given'):
        file_chunks(value=67, path=str(file_path))


def test_neg_file_chunks_wrong_value(tmp_path: Path) -> None:
    file_path = tmp_path / 'test.py'
    file_path.write_text('The wolf', encoding='utf-8')

    with pytest.raises(ChunksError, match='positive'):
        file_chunks(mode='len', value=-67, path=str(file_path))


def test_neg_file_chunks_no_file(tmp_path: Path) -> None:
    file_path = tmp_path / 'test.py'

    with pytest.raises(FileReadError, match='not found'):
        file_chunks(mode='len', value=67, path=str(file_path))
