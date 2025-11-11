# valutatrade_hub/infra/settings.py
import os
from datetime import timedelta

class SettingsLoader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

            # Основные параметры
            cls._instance.DATA_DIR = "data"
            cls._instance.USERS_FILE = os.path.join(cls._instance.DATA_DIR, "users.json")
            cls._instance.PORTFOLIOS_FILE = os.path.join(cls._instance.DATA_DIR, "portfolios.json")
            cls._instance.RATES_FILE = os.path.join(cls._instance.DATA_DIR, "rates.json")

            # ExchangeRate-API ключ
            cls._instance.EXCHANGERATE_API_KEY = os.getenv(
                "EXCHANGERATE_API_KEY",
                "1a4a95b327278c18d57643bb"  # по умолчанию твой ключ
            )

            # Таймаут сетевых запросов
            cls._instance.REQUEST_TIMEOUT = 10  # секунд

            # TTL кэша для rates.json (например, 5 минут)
            cls._instance.RATES_TTL_SECONDS = 300

            # Базовая валюта
            cls._instance.BASE_CURRENCY = "USD"

        return cls._instance

    def get(self, key, default=None):
        return getattr(self, key, default)

    def reload(self):
        # В реальности можно перечитать переменные окружения или config-файл
        self.__class__._instance = None
        return SettingsLoader()


