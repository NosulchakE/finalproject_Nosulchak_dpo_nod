# valutatrade_hub/infra/settings.py
import os

class SettingsLoader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

            # общие настройки проекта
            cls._instance.DATA_DIR = "data"
            cls._instance.LOGS_DIR = "logs"
            
            # Файлы данных
            cls._instance.USERS_FILE = os.path.join(cls._instance.DATA_DIR, "users.json")
            cls._instance.PORTFOLIOS_FILE = os.path.join(cls._instance.DATA_DIR, "portfolios.json")
            cls._instance.RATES_FILE = os.path.join(cls._instance.DATA_DIR, "rates.json")
            cls._instance.EXCHANGE_RATES_FILE = os.path.join(cls._instance.DATA_DIR, "exchange_rates.json")
            
            # Файлы логов
            cls._instance.ACTIONS_LOG = os.path.join(cls._instance.LOGS_DIR, "actions.log")
            
            # Настройки API (для parser_service)
            cls._instance.EXCHANGERATE_API_KEY = os.getenv("EXCHANGERATE_API_KEY", "")
            cls._instance.BASE_CURRENCY = "USD"
            
            #  валюты
            cls._instance.SUPPORTED_CURRENCIES = ["USD", "EUR", "GBP", "RUB", "BTC", "ETH", "SOL"]

        return cls._instance

    def get(self, key, default=None):
        return getattr(self, key, default)





