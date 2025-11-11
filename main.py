# main.py
import sys
import logging
from valutatrade_hub.cli.interface import main as cli_main
from valutatrade_hub.logging_config import setup_logging


def main():
    """Точка входа в приложение ValutaTradeHub."""
    setup_logging()

    try:
        cli_main()
    except Exception as e:
        logging.exception("Unhandled exception in CLI")
        print(f"Произошла ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
