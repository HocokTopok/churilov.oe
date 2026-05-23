import sys

from src.config import load_config
from src.app import run
from src.exceptions import AIAssistantError


UNKNOWN_ERROR_MESSAGE = 'CRITICAL ERROR: unexpected error'


def main() -> None:
    try:
        cnf = load_config()
        run(cnf)
    except AIAssistantError as error:
        print(error)
        sys.exit(1)
    except Exception as error:
        print(f'{UNKNOWN_ERROR_MESSAGE}: {error}')
        sys.exit(1)


if __name__ == '__main__':
    main()