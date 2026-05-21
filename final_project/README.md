# Итоговый проект "GigaVibeMiptCode"

GigaVibeMiptCode — консольный AI-ассистент с поддержкой OpenAI-compatible API.  
Проект позволяет отправлять сообщения в LLM, хранить историю диалога, ограничивать длину контекста, подставлять содержимое файлов в запрос, обрабатывать большие файлы по чанкам и получать вывод ответа модели прямо во время генерации.

## Основной функционал

С программой можно взаимодействовать через консольный интерфейс:

- отправлять обычные текстовые запросы к модели;
- получать ответы модели в streaming-режиме;
- завершать программу командой `\q`;
- очищать историю диалога и экран командой `/reset`;
- подставлять содержимое файлов в запрос через синтаксис `@::path/to/file::`;
- обрабатывать большие файлы по частям через команду `/file_chunk`;
- делить файл на чанки по абзацам: `/file_chunk paragraph=3 file.txt`;
- делить файл на чанки по количеству символов: `/file_chunk len=150 file.txt`;
- запускать автоматическую обработку всех чанков без ожидания Enter через флаг `-y`;
- настраивать модель, API-адрес, ключ, температуру, лимиты контекста и системный промпт через `config.yaml` или переменные окружения;
- ограничивать историю сообщений по количеству сообщений и по суммарному числу символов.

## Структура проекта

```text
project/
├── config.yaml (нужно самому добавить)
├── htmlcov/
├── src/
│   ├── __init__.py
│   ├── app.py
│   ├── client.py
│   ├── config.py
│   ├── context_manager.py
│   ├── exceptions.py
│   ├── file_attachment.py
│   ├── file_chunks.py
│   └── main.py
└── tests/
    ├── test_app.py
    ├── test_client.py
    ├── test_config.py
    ├── test_context_manager.py
    ├── test_file_attachment.py
    ├── test_file_chunks.py
    └── test_main.py
```

## Описание файлов

- `src/main.py` — точка входа: загружает конфиг, запускает приложение, обрабатывает критические ошибки
- `src/app.py` — основной консольный цикл
- `src/client.py` — клиент для OpenAI-compatible API: отправка запросов и streaming-ответы
- `src/config.py` — загрузка настроек из `config.yaml` и переменных окружения
- `src/context_manager.py` — хранение истории диалога и ограничение контекста
- `src/file_attachment.py` — подстановка содержимого файлов через `@::path::`
- `src/file_chunks.py` — чтение файла и деление на чанки по абзацам или символам
- `src/exceptions.py` — пользовательские исключения проекта
- `tests/` — тесты для основных модулей
- `htmlcov/` — HTML-отчёт покрытия тестами
- `config.yaml` — локальный файл настроек приложения (нужно добавить самому)

## Установка, настройка и запуск

Перейдите в папку проекта:

```bash
cd final_project/project
```

Установите зависимости:

```bash
pip install openai pyyaml pytest pytest-cov mypy ruff types-PyYAML
```

Создайте файл `config.yaml` в папке `final_project/project`:

```yaml
api_host: http://localhost:11434/v1/
api_key: ollama
model: qwen2.5-coder:7b
temperature: 0.3
limit_messages: 20
limit_chars: 10000
system_prompt: Отвечай кратко и понятно
```

Если Ollama-сервер не запущен, запустите его:

```bash
ollama serve
```

В другом терминале скачайте модель:

```bash
ollama pull qwen2.5-coder:7b
```

Запустите приложение из папки `final_project/project`:

```bash
python -m src.main
```

После запуска появится интерактивный ввод:

```text
>>> 
```

Примеры команд:

```text
>>> Привет
>>> /reset
>>> /file_chunk len=150 test.txt
>>> /file_chunk paragraph=3 -y test.txt
>>> \q
```

Также уже сделан отчёт покрытия (на macOS):

```bash
open htmlcov/index.html
```