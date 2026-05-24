from src.app import is_file_chunk_command, parse_chunk_parameters


def test_pos_is_file_chunk_command_default() -> None:
    assert is_file_chunk_command('/file_chunk')
    assert is_file_chunk_command('/filechunk')


def test_pos_is_file_chunk_command_with_parameters() -> None:
    assert is_file_chunk_command('/file_chunk /path/file.txt')
    assert is_file_chunk_command('/file_chunk -y')
    assert is_file_chunk_command('/file_chunk -y /path/file.txt')
    assert is_file_chunk_command('/file_chunk paragraph=3')
    assert is_file_chunk_command('/file_chunk len=150')
    assert is_file_chunk_command('/file_chunk paragraph=3 -y')
    assert is_file_chunk_command('/file_chunk len=150 test.txt')
    assert is_file_chunk_command('/file_chunk paragraph=3 -y test.txt')


def test_neg_is_file_chunk_command() -> None:
    assert not is_file_chunk_command('/file_chunk_bad')
    assert not is_file_chunk_command('/file_chunk len=abc')
    assert not is_file_chunk_command('/file_chunk paragraph=-3')
    assert not is_file_chunk_command('/file_chunk paragraph=3 len=150')
    assert not is_file_chunk_command('hello')
    assert not is_file_chunk_command('')


def test_pos_parse_chunk_parameters_default() -> None:
    result = parse_chunk_parameters('/file_chunk')
    assert result == (None, None, None, False)


def test_pos_parse_chunk_parameters_paragraph() -> None:
    result = parse_chunk_parameters('/file_chunk paragraph=3')
    assert result == ('paragraph', 3, None, False)


def test_pos_parse_chunk_parameters_len() -> None:
    result = parse_chunk_parameters('/file_chunk len=150')
    assert result == ('len', 150, None, False)


def test_pos_parse_chunk_parameters_auto() -> None:
    result = parse_chunk_parameters('/file_chunk paragraph=3 -y')
    assert result == ('paragraph', 3, None, True)


def test_pos_parse_chunk_parameters_path() -> None:
    result = parse_chunk_parameters('/file_chunk len=150 -y test.txt')
    assert result == ('len', 150, 'test.txt', True)
