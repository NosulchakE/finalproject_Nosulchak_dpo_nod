# valutatrade_hub/infra/settings.py
import os

class SettingsLoader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

            # Только общие настройки проекта
            cls._instance.DATA_DIR = "data"
            cls._instance.USERS_FILE = os.path.join(cls._instance.DATA_DIR, "users.json")
            cls._instance.PORTFOLIOS_FILE = os.path.join(cls._instance.DATA_DIR, "portfolios.json")
            
            # Больше не дублируем настройки парсера - они в ParserConfig

        return cls._instance

    def get(self, key, default=None):
        return getattr(self, key, default)



