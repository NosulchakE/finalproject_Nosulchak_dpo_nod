# valutatrade_hub/parser_service/config.py
import os
from dataclasses import dataclass, field
from typing import Dict, Tuple

@dataclass
class ParserConfig:
    # Ключ загружается из переменной окружения
    EXCHANGERATE_API_KEY: str = field(default_factory=lambda: os.getenv("EXCHANGERATE_API_KEY", ""))

    # Эндпоинт ExchangeRate-API
    EXCHANGERATE_API_URL: str = "https://v6.exchangerate-api.com/v6"

    # Списки валют
    BASE_CURRENCY: str = "USD"
    FIAT_CURRENCIES: Tuple[str, ...] = ("EUR", "GBP", "RUB")
    CRYPTO_CURRENCIES: Tuple[str, ...] = ("BTC", "ETH", "SOL")

    # Пути
    RATES_FILE_PATH: str = "data/rates.json"
    HISTORY_FILE_PATH: str = "data/exchange_rates.json"

    # Сетевые параметры
    REQUEST_TIMEOUT: int = 10

    # Для возможной кастомизации (например, сопоставления тикеров, если понадобится)
    CUSTOM_CRYPTO_MAP: Dict[str, str] = field(default_factory=dict)






