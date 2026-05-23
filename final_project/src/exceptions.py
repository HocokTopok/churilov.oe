class AIAssistantError(Exception):
    """Базовый класс исключения, от которого наследуются остальные"""

class ConfigError(AIAssistantError):
    """Ошибка при работе с конфигурированием данных"""

class FileReadError(AIAssistantError):
    """Ошибка при чтении файла"""

class ChunksError(AIAssistantError):
    """Ошибка при работе с чанками"""

class LLMClientError(AIAssistantError):
    """Ошибка при работе с моделью"""