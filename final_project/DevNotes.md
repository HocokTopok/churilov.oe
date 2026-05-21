# DevNotes

Здесь я записал некоторые моменты в коде, которые выглядят странно. Чтобы потом на ревью не прояснять некоторые моменты, я объясню их сразу здесь

## config.py: 

```python
def get_system_prompt(data: dict[str, Any], yaml_name: str = "system_prompt") -> str | None:
  value: Any = data.get(yaml_name)

  return value if value is None else str(value)
```

Здесь я добавил ветвление, потому что хотел предусмотреть случай, если на вход дадут системный промпт 123. До этого код бы вернул число int и положил в str поле в Config. Чтобы Pylance (и наверное mypy) не ругались я перестарховался таким образом

## file_attechment.py:

```python
PATH_PATTERN = "@::(.+?)::"
```

Здесь я использовал регулярки, я не знаю можно ли их было использовать, но если что я со школы с ними знаком и, как мне показалось, тут они идеально подходят. Надеюсь на это и был расчет

## test_file_attachment.py

```python
def test_neg_read_file(tmp_path):
  file_path = tmp_path / "missing.py"

  with pytest.raises(FileAttachmentError, match="not found"):
    read_file(str(file_path))
```

Здесь создание файла выглядит бесполезным, но если на компьютере случайно существует такой файл и мы явно так не пропишем, то тест сломается

## file_chunks.py

```python
def split_by_paragraph(text: str, value: int = DEFAULT_SPLIT_VALUE) -> list[str]:
  chunks: list[str] = []

  paragraphs = [par for par in text.split("\n") if par.strip()]
  for i in range(0, len(paragraphs), value):
    chunks.append("\n".join(paragraphs[i:(i + value)]))
  
  return chunks
```

Здесь я сделал [par for par in text.split("\n") if par.strip()] для того, чтобы пропустить все пустые абзацы, мне показалось это логичным

## context_manager.py

```python
def count_chars(self) -> int:
  return sum(len(msg[CONTENT_KEY]) for msg in self.messages)
```

Я не стал добавлять в количество сообщений и количество символов system_prompt, потому что тогда логика с удалением сообщений станет сложной. Например, что делать если у системном промпте символов уже больше, чем разрешено...

## client.py

```python
response = self.client.chat.completions.create(
  model=self.model,
  messages=cast(list[ChatCompletionMessageParam], messages),
  temperature=self.temperature
)
```

Pylance ругался, что тип list[dict[str, str]] слишком общий и я его просто скастил в абракадабру из openai

## app.py

```python
CHUNK_COMMAND_PATTERN = r"^/(file_chunk|filechunk)(\s+(paragraph|len)=\d+)?(\s+-y)?(\s+(?!(paragraph|len)=)\S+)?$"
```

Здесь я добавил регулярку, чтобы задать определенный шаблон для команды file_chunk, сейчас поддерживаются варианты ниже. Если коротко, то я поддержал определенный порядок параметров и для каждого параметра в () указаны возможны варианты через |. Также используюся \d+ для цифр и \S+ для НЕпробелов.

/file_chunk
/filechunk
/file_chunk -y
/file_chunk paragraph=3
/file_chunk len=150
/file_chunk paragraph=3 -y
/file_chunk len=150 -y
/file_chunk /path/to/file.txt
/file_chunk paragraph=3 -y /path/to/file.txt

А еще у меня все сломалось на следующем тесте

/file_chunk len=abс

Поэтому пришлось добавить (?!(paragraph|len)=)\S+), чтобы не принимало len=abc за path

## testing

Также решил прикрепить сюда тесты, которые я провел вручную

oleg@MacBook-Air-Oleg project % python -m src.main
>>> /file_chunk len=3 text.txt      
Error: file text.txt not found
>>> /file_chunk len=3 test.txt
Принято. Что нужно сделать для каждого фрагмента?
>>> выведи сумму цифр
Принято. Начинаю обработку:
Сумма цифр в числе 123 равна:

1 + 2 + 3 = **6**
>>> 
Сумма цифр числа 456 равна:

4 + 5 + 6 = 15
>>> 
Сумма цифр в числе 789 равна:

\(7 + 8 + 9 = 24\)
>>> 
Сумма цифр в числе 0 равна 0.
>>> 
Обработка файла завершена
>>> 
>>> бу
Извините, но я не могу понять ваше сообщение. Пожалуйста, напишите что-то более конкре^C
>>> Посчитай сумму цифр @::test.txt::    
Сумма цифр в числе 1234567890 равна:

1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 + 0 = **45**
>>> /reset 

>>> какое было последнее сообщение
Мне жаль, но я не могу сказать, что было последнее сообщение, потому что я являюсь искусственным интеллектом и не имею способности отслеживать историю нашего общения. Каждый раз, когда мы начинаем новый диалог^C
>>> 2 + 2
4
>>> какое было последнее сообщение
Последнее сообщение - это ваше текущее запрос "какое было последнее сообщение".
>>> тогда предпоследнее
Извините за путаницу. Предпоследним сообщением был вопрос "2 + 2". Ответ на который был "4".
>>> \q
oleg@MacBook-Air-Oleg project % 

## pytest

oleg@MacBook-Air-Oleg project % pytest
================================ test session starts ================================
platform darwin -- Python 3.13.12, pytest-9.0.3, pluggy-1.6.0
rootdir: /Users/oleg/VS_Code_files/churilov.oe/final_project/project
configfile: pyproject.toml
testpaths: tests
plugins: anyio-4.13.0
collected 43 items                                                                  

tests/test_app.py ........                                                    [ 18%]
tests/test_client.py ...                                                      [ 25%]
tests/test_config.py ...........                                              [ 51%]
tests/test_coxtent_manager.py ......                                          [ 65%]
tests/test_file_attachment.py ....                                            [ 74%]
tests/test_file_chunks.py ........                                            [ 93%]
tests/test_main.py ...                                                        [100%]

================================ 43 passed in 0.84s =================================

## ruff & mypy

oleg@MacBook-Air-Oleg churilov.oe % ruff check final_project/project --config final_project/ruff.toml
All checks passed!
oleg@MacBook-Air-Oleg churilov.oe % mypy final_project/project 
Success: no issues found in 16 source files

## htmlcov

Coverage report: 71%