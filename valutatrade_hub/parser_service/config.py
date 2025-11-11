import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

@dataclass
class ParserConfig:
    EXCHANGERATE_API_KEY: str = os.getenv("EXCHANGERATE_API_KEY")
    BASE_CURRENCY: str = "USD"
    FIAT_CURRENCIES: tuple = ("EUR", "GBP", "RUB")
    CRYPTO_CURRENCIES: tuple = ("BTC", "ETH", "SOL")
    CRYPTO_ID_MAP: dict = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
    }
    RATES_FILE_PATH: str = "data/rates.json"
    HISTORY_FILE_PATH: str = "data/exchange_rates.json"
    REQUEST_TIMEOUT: int = 10




