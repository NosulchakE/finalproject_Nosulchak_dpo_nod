import os
from dataclasses import dataclass

@dataclass
class ParserConfig:
    # Ключ ExchangeRate-API
    EXCHANGERATE_API_KEY: str = os.getenv("EXCHANGERATE_API_KEY", "1a4a95b327278c18d57643bb")

    # URL
    EXCHANGERATE_API_URL: str = "https://v6.exchangerate-api.com/v6"

    # Списки валют
    BASE_CURRENCY: str = "USD"
    FIAT_CURRENCIES: tuple = ("EUR", "GBP", "RUB")
    CRYPTO_CURRENCIES: tuple = ("BTC", "ETH", "SOL")

    # Пути к JSON
    RATES_FILE_PATH: str = "data/rates.json"
    HISTORY_FILE_PATH: str = "data/exchange_rates.json"

    # Сетевые параметры
    REQUEST_TIMEOUT: int = 10


