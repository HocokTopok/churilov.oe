from src.config import Config

SYSTEM_ROLE = 'system'

CONTENT_KEY = 'content'
ROLE_KEY = 'role'


class ContextManager:
    def __init__(self, cnf: Config):
        self.limit_chars: int | None = cnf.limit_chars
        self.limit_messages: int | None = cnf.limit_messages
        self.system_prompt: str | None = cnf.system_prompt
        self.messages: list[dict[str, str]] = []


    def count_chars(self) -> int:
        return sum(len(msg[CONTENT_KEY]) for msg in self.messages)


    def cut_context(self) -> None:
        if self.limit_messages is not None:
            while len(self.messages) > self.limit_messages:
                self.messages.pop(0)

        if self.limit_chars is not None:
            while self.count_chars() > self.limit_chars:
                if len(self.messages) > 1:
                    self.messages.pop(0)
                else:
                    self.messages[0][CONTENT_KEY] = self.messages[0][CONTENT_KEY][
                        -self.limit_chars:
                        ]
                    break


    def add_message(self, role: str, text: str) -> None:
        new_message = {ROLE_KEY: role, CONTENT_KEY: text}
        self.messages.append(new_message)
        self.cut_context()


    def delete_last(self) -> None:
        self.messages.pop(0)


    def get_messages(self) -> list[dict[str, str]]:
        if self.system_prompt is not None:
            return [
                {ROLE_KEY: SYSTEM_ROLE, CONTENT_KEY: self.system_prompt},
                *self.messages
            ]
        return self.messages.copy()


    def reset(self) -> None:
        self.messages.clear()