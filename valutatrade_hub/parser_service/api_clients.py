# valutatrade_hub/parser_service/api_clients.py
from abc import ABC, abstractmethod
from typing import Dict
import requests
from .config import ParserConfig
from valutatrade_hub.core.exceptions import ApiRequestError

CRYPTO_ID_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana"
}
# создаем абстрактный базовый класс в соответствии с ТЗ
class BaseApiClient(ABC):
    """Абстрактный базовый класс для всех API клиентов."""

    @abstractmethod
    def fetch_rates(self) -> Dict[str, float]:
        """Возвращает словарь курсов в формате {'USD_BTC': 59337.21}"""
        pass

# клиент CoinGecko наследуется из АВС
class CoinGeckoClient(BaseApiClient):
    """Клиент для CoinGecko (криптовалюты)"""

    def __init__(self):
        self.config = ParserConfig()
        self.timeout = self.config.REQUEST_TIMEOUT
        self.ids = ','.join(CRYPTO_ID_MAP.values())
        self.vs_currency = self.config.BASE_CURRENCY.lower()
        self.url = f"https://api.coingecko.com/api/v3/simple/price?ids={self.ids}&vs_currencies={self.vs_currency}"

    def fetch_rates(self) -> Dict[str, float]:
        """Получаем курсы криптовалют"""
        try:
            response = requests.get(self.url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            rates = {}
            for code, coingecko_id in CRYPTO_ID_MAP.items():
                if coingecko_id in data and self.vs_currency in data[coingecko_id]:
                    key = f"{self.config.BASE_CURRENCY}_{code}"
                    rates[key] = data[coingecko_id][self.vs_currency]
            return rates
        except requests.RequestException as e:
            print(f"[CoinGecko] Ошибка сети: {e}. Используем заглушку.")
            return self._mock_rates()
        except Exception as e:
            print(f"[CoinGecko] Неожиданная ошибка: {e}. Используем заглушку.")
            return self._mock_rates()

    def _mock_rates(self) -> Dict[str, float]:
        """Возвращает тестовые данные"""
        print("[CoinGecko] Используются тестовые данные")
        return {f"{self.config.BASE_CURRENCY}_{code}": 100.0 + i*50
                for i, code in enumerate(CRYPTO_ID_MAP.keys(), 1)}

# клиент ExchangeRate-API наследуется из АВС
class ExchangeRateApiClient(BaseApiClient):
    """Клиент для ExchangeRate-API (фиатные валюты)"""

    def __init__(self):
        self.config = ParserConfig()
        self.base_url = f"{self.config.EXCHANGERATE_API_URL}/{self.config.EXCHANGERATE_API_KEY}/latest/{self.config.BASE_CURRENCY}"
        self.timeout = self.config.REQUEST_TIMEOUT

    def fetch_rates(self) -> Dict[str, float]:
        """Получаем курсы фиатных валют"""
        if not self.config.EXCHANGERATE_API_KEY:
            print("[ExchangeRate] API ключ не задан. Используем заглушку.")
            return self._mock_rates()
        try:
            response = requests.get(self.base_url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            if data.get("result") != "success":
                raise ApiRequestError(f"Ошибка API: {data.get('error-type', 'Unknown')}")
            rates = {}
            for code, rate in data.get("conversion_rates", {}).items():
                if code != self.config.BASE_CURRENCY:
                    key = f"{self.config.BASE_CURRENCY}_{code}"
                    rates[key] = rate
            return rates
        except requests.RequestException as e:
            print(f"[ExchangeRate] Ошибка сети: {e}. Используем заглушку.")
            return self._mock_rates()
        except Exception as e:
            print(f"[ExchangeRate] Неожиданная ошибка: {e}. Используем заглушку.")
            return self._mock_rates()

    def _mock_rates(self) -> Dict[str, float]:
        """Возвращает тестовые данные"""
        print("[ExchangeRate] Используются тестовые данные")
        return {f"{self.config.BASE_CURRENCY}_{code}": 0.9 + i*0.1
                for i, code in enumerate(self.config.FIAT_CURRENCIES, 1)}






