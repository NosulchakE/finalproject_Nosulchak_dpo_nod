# valutatrade_hub/logging_config.py
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging():
    """логированиу для всего приложения"""
    LOG_FILE = Path("logs/actions.log")
    LOG_FILE.parent.mkdir(exist_ok=True, parents=True)
    
    # Настройка корневого логгера (а не только "valutatrade")
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Форматтер 
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s", 
        datefmt="%Y-%m-%dT%H:%M:%S"
    )
    
    # Файловый обработчик 
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=1_000_000, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    #  консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Убираем старые обработчики и добавляем новые
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


