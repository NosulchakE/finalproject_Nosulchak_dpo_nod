import json
from pathlib import Path
from typing import Any

class SettingsLoader:
    """
    Singleton для конфигурации проекта.

    Реализован через __new__ для простоты и читаемости:
    - гарантирует единственный экземпляр в приложении,
    - легко использовать в любом месте через import,
    - при повторном импорте не создаются новые объекты.
    """

    _instance = None

    def __new__(cls, config_path: str = "config.json"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config_path = Path(config_path)
            cls._instance._load_settings()
        return cls._instance

    def _load_settings(self):
        """Загрузка конфигурации из JSON, дефолтные значения при отсутствии файла"""
        if self._config_path.exists():
            with open(self._config_path, "r", encoding="utf-8") as f:
                self._config = json.load(f)
        else:
            # Дефолтные значения
            self._config = {
                "DATA_PATH": "data/",
                "USERS_JSON": "data/users.json",
                "PORTFOLIOS_JSON": "data/portfolios.json",
                "RATES_JSON": "data/rates.json",
                "BASE_CURRENCY": "USD",
                "RATES_TTL_SECONDS": 300,
                "LOG_PATH": "logs/valutatrade.log",
            }

    def get(self, key: str, default: Any = None) -> Any:
        """Получение значения по ключу"""
        return self._config.get(key, default)

    def reload(self):
        """Перезагрузка конфигурации из файла"""
        self._load_settings()
