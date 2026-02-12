# valutatrade_hub/parser_service/config.py
import os
from dataclasses import dataclass, field
from typing import Dict, Tuple
from dotenv import load_dotenv  

load_dotenv()  # загружает .env файл

@dataclass
class ParserConfig:
    # Ключ загружается из переменной окружения
    EXCHANGERATE_API_KEY: str = field(default_factory=lambda: os.getenv("EXCHANGERATE_API_KEY", ""))
    
    # Эндпоинт ExchangeRate-API
    EXCHANGERATE_API_URL: str = "https://v6.exchangerate-api.com/v6"
    
    # Эндпоинт CoinGecko API
    COINGECKO_API_URL: str = "https://api.coingecko.com/api/v3/simple/price"
    
    # Списки валют
    BASE_CURRENCY: str = "USD"
    FIAT_CURRENCIES: Tuple[str, ...] = ("EUR", "GBP", "RUB")
    CRYPTO_CURRENCIES: Tuple[str, ...] = ("BTC", "ETH", "SOL")
    
    # Маппинг тикеров на ID в CoinGecko
    CRYPTO_ID_MAP: Dict[str, str] = field(default_factory=lambda: {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana"
    })
    
    # Пути (оставляем относительные пути)
    RATES_FILE_PATH: str = field(default_factory=lambda: "data/rates.json")
    HISTORY_FILE_PATH: str = field(default_factory=lambda: "data/exchange_rates.json")
    
    # Сетевые параметры
    REQUEST_TIMEOUT: int = 10
    
    # Для возможной кастомизации
    CUSTOM_CRYPTO_MAP: Dict[str, str] = field(default_factory=dict)







