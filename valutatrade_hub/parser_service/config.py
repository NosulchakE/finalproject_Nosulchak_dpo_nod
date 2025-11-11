# valutatrade_hub/parser_service/config.py
import os
from dataclasses import dataclass

@dataclass
class ParserConfig:
    # Ключ загружается из переменной окружения, можно подставить напрямую для теста
    EXCHANGERATE_API_KEY: str = os.getenv("EXCHANGERATE_API_KEY", "1a4a95b327278c18d57643bb")

    # Эндпоинт ExchangeRate-API
    EXCHANGERATE_API_URL: str = "https://v6.exchangerate-api.com/v6"

    # Валюты
    BASE_CURRENCY: str = "USD"
    FIAT_CURRENCIES: tuple = ("EUR", "GBP", "RUB")
    CRYPTO_CURRENCIES: tuple = ("BTC", "ETH", "SOL")

    # Пути к файлам
    RATES_FILE_PATH: str = "data/rates.json"
    HISTORY_FILE_PATH: str = "data/exchange_rates.json"

    # Таймаут для запросов
    REQUEST_TIMEOUT: int = 10
