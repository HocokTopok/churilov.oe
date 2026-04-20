import json
from datetime import UTC, datetime, timedelta
from functools import wraps
from typing import Any, ParamSpec, Protocol, TypeVar
from urllib.request import urlopen

INVALID_CRITICAL_COUNT = "Breaker count must be positive integer!"
INVALID_RECOVERY_TIME = "Breaker recovery time must be positive integer!"
VALIDATIONS_FAILED = "Invalid decorator args."
TOO_MUCH = "Too much requests, just wait."


P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)


class CallableWithMeta(Protocol[P, R_co]):
    __name__: str
    __module__: str

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...


class BreakerError(Exception):
    def __init__(
        self,
        func_name: str,
        block_time: datetime,
    ):
        self.func_name = func_name
        self.block_time = block_time
        super().__init__(TOO_MUCH)


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int = 5,
        time_to_recover: int = 30,
        triggers_on: type[Exception] = Exception,
    ):
        errors: list[Exception] = []

        if not isinstance(critical_count, int) or critical_count <= 0:
            errors.append(ValueError(INVALID_CRITICAL_COUNT))

        if not isinstance(time_to_recover, int) or time_to_recover <= 0:
            errors.append(ValueError(INVALID_RECOVERY_TIME))

        if errors:
            raise ExceptionGroup(VALIDATIONS_FAILED, errors)

        self.critical_count = critical_count
        self.time_to_recover = time_to_recover
        self.triggers_on = triggers_on
        self.state: bool = True
        self.fails: int = 0
        self.shutdown_start: datetime = datetime.now(UTC)

    def __call__(self, func: CallableWithMeta[P, R_co]) -> CallableWithMeta[P, R_co]:
        @wraps(func)
        def inner(*args: P.args, **kwargs: P.kwargs) -> R_co:
            self.check_shutdown(func)

            try:
                res = func(*args, **kwargs)

            except self.triggers_on as er:
                self.handle_triggers_on(func, er)
                raise

            else:
                self.fails = 0
                return res

        return inner

    def check_shutdown(self, func: CallableWithMeta[P, R_co]) -> None:
        if not self.state:
            current_time = datetime.now(UTC)

            if current_time - self.shutdown_start >= timedelta(seconds=self.time_to_recover):
                self.state = True
                self.fails = 0

            else:
                func_name = f"{func.__module__}.{func.__name__}"
                raise BreakerError(func_name, self.shutdown_start)

    def handle_triggers_on(self, func: CallableWithMeta[P, R_co], error: Exception) -> None:
        self.fails += 1
        if self.fails >= self.critical_count:
            self.state = False
            func_name = f"{func.__module__}.{func.__name__}"
            self.shutdown_start = datetime.now(UTC)
            raise BreakerError(func_name, self.shutdown_start) from error
        raise error


circuit_breaker = CircuitBreaker(5, 30, Exception)


# @circuit_breaker
def get_comments(post_id: int) -> Any:
    """
    Получает комментарии к посту

    Args:
        post_id (int): Идентификатор поста

    Returns:
        list[dict[int | str]]: Список комментариев
    """
    response = urlopen(f"https://jsonplaceholder.typicode.com/comments?postId={post_id}")
    return json.loads(response.read())


if __name__ == "__main__":
    comments = get_comments(1)
