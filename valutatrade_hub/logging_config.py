# valutatrade_hub/logging_config.py
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging():
    """Настройка логирования для всего приложения"""
    
    # Создаем папку logs
    os.makedirs("logs", exist_ok=True)
    
    # Настройка корневого логгера
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Формат по ТЗ: timestamp levelname message
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S"
    )
    
    # Файловый обработчик с ротацией не более 5
    file_handler = RotatingFileHandler(
        "logs/actions.log",
        maxBytes=1_000_000,
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Очищаем старые обработчики и добавляем новые
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)



