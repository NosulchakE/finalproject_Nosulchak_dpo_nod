import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FILE = Path("logs/actions.log")
LOG_FILE.parent.mkdir(exist_ok=True, parents=True)  # Создать папку logs, если нет

# Настройка логгера
logger = logging.getLogger("valutatrade")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%S"
)

# Ротация: максимум 5 файлов по 1MB каждый
handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=5, encoding="utf-8")
handler.setFormatter(formatter)
logger.addHandler(handler)
