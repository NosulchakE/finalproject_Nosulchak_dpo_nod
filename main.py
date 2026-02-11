# main.py
import logging
from valutatrade_hub.cli.interface import run_interactive_cli
from valutatrade_hub.logging_config import setup_logging  # ИСПОЛЬЗУЕМ ОБЩУЮ НАСТРОЙКУ


def main():
    # Настройка логирования для всего приложения
    setup_logging()
    
    #  логгер после настройки
    logger = logging.getLogger("Main")
    logger.info("Запуск CLI для управления валютным портфелем")
    
    run_interactive_cli()


if __name__ == "__main__":
    main()











