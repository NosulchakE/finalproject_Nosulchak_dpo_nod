# main.py
import logging
from valutatrade_hub.cli.interface import run_interactive_cli


def setup_logging():
    """
    настройка логирования для всего приложения.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )


def main():
    setup_logging()
    logger = logging.getLogger("Main")

    logger.info("Запуск CLI для управления валютным портфелем")
    run_interactive_cli()


if __name__ == "__main__":
    main()











