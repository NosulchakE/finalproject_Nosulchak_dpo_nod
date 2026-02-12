# valutatrade_hub/parser_service/api_clients.py
from abc import ABC, abstractmethod
from typing import Dict
import requests
import logging
from .config import ParserConfig

logger = logging.getLogger(__name__)


class BaseApiClient(ABC):
    """Базовый абстрактный класс для API клиентов"""
    
    def __init__(self):
        self.config = ParserConfig()
        self.timeout = self.config.REQUEST_TIMEOUT
    
    @abstractmethod
    def get_rates(self) -> Dict[str, float]:
        """Получить курсы валют"""
        pass
    
    @abstractmethod
    def _get_mock_rates(self) -> Dict[str, float]:
        """Тестовые данные на случай ошибки"""
        pass


class ExchangeRateAPI(BaseApiClient):
    """Клиент для ExchangeRate-API (только фиат)"""
    
    def __init__(self):
        super().__init__()  # вызвать родительский __init__
        self.base_url = f"{self.config.EXCHANGERATE_API_URL}/{self.config.EXCHANGERATE_API_KEY}/latest/{self.config.BASE_CURRENCY}"
    
    def get_rates(self) -> Dict[str, float]:
        try:
            if not self.config.EXCHANGERATE_API_KEY:
                logger.warning("API ключ не установлен, тестовые данные")
                return self._get_mock_rates()
            
            logger.info("Запрос к ExchangeRate-API...")
            response = requests.get(self.base_url, timeout=self.timeout)
            
            if response.status_code != 200:
                logger.warning(f"HTTP ошибка {response.status_code}")
                return self._get_mock_rates()
            
            data = response.json()
            
            if data.get("result") == "success":
                rates = data.get("conversion_rates", {})
                # Только фиатные валюты
                fiat_rates = {
                    curr: rates[curr] 
                    for curr in self.config.FIAT_CURRENCIES 
                    if curr in rates
                }
                logger.info(f"Получено {len(fiat_rates)} фиатных курсов")
                return fiat_rates
            
            return self._get_mock_rates()
            
        except Exception as e:
            logger.error(f"Ошибка ExchangeRate-API: {e}")
            return self._get_mock_rates()
    
    def _get_mock_rates(self) -> Dict[str, float]:
        return {"EUR": 0.92, "GBP": 0.79, "RUB": 92.5}


class CoinGeckoAPI(BaseApiClient):
    """Клиент для CoinGecko API (криптовалюты)"""
    
    def __init__(self):
        super().__init__()  # вызвать родительский __init__
    
    def get_rates(self) -> Dict[str, float]:
        try:
            coin_ids = ",".join(self.config.CRYPTO_ID_MAP.values())
            url = f"{self.config.COINGECKO_API_URL}?ids={coin_ids}&vs_currencies=usd"
            
            logger.info("Запрос к CoinGecko API...")
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code != 200:
                logger.warning(f"HTTP ошибка {response.status_code}")
                return self._get_mock_rates()
            
            data = response.json()
            
            rates = {}
            for ticker, coin_id in self.config.CRYPTO_ID_MAP.items():
                if coin_id in data and "usd" in data[coin_id]:
                    rates[ticker] = data[coin_id]["usd"]
            
            logger.info(f"Получено {len(rates)} курсов криптовалют")
            return rates
            
        except Exception as e:
            logger.error(f"Ошибка CoinGecko: {e}")
            return self._get_mock_rates()
    
    def _get_mock_rates(self) -> Dict[str, float]:
        return {"BTC": 59337.21, "ETH": 3720.00, "SOL": 145.12}







