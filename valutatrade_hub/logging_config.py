# valutatrade_hub/logging_config.py
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os


def setup_logging():
    """Настройка логирования для всего приложения согласно (ТЗ!!)"""
    
    # Создаем папку logs если нет
    LOGS_DIR = "logs"
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    # Файл для действий согласно ТЗ
    ACTIONS_LOG = Path(LOGS_DIR) / "actions.log"
    
    # Настройка логгера для действий (декоратора)
    actions_logger = logging.getLogger("valutatrade.actions")
    actions_logger.setLevel(logging.INFO)
    actions_logger.propagate = False  # Не передавать родительским логгерам
    
    # Форматтер: строковый формат согласно ТЗ
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S"
    )
    
    # Обработчик с ротацией согласно ТЗ
    file_handler = RotatingFileHandler(
        ACTIONS_LOG,
        maxBytes=1_000_000,  # 1MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Консольный обработчик для отладки
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Убираем старые обработчики и добавляем новые
    actions_logger.handlers.clear()
    actions_logger.addHandler(file_handler)
    actions_logger.addHandler(console_handler)
    
    # Настройка корневого логгера для всего приложения
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Если нужны логи всего приложения в отдельный файл
    app_logger = logging.getLogger("valutatrade")
    app_logger.setLevel(logging.DEBUG)  # DEBUG для отладки согласно ТЗ
    
    return actions_logger



