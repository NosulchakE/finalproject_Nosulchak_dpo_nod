# valutatrade_hub/parser_service/api_clients.py
import requests
from typing import Dict, Any

from .config import ParserConfig
from valutatrade_hub.core.exceptions import ApiRequestError


class ExchangeRateAPI:
    """Клиент для работы с ExchangeRate-API"""
    
    def __init__(self):
        self.config = ParserConfig()
        self.base_url = f"{self.config.EXCHANGERATE_API_URL}/{self.config.EXCHANGERATE_API_KEY}/latest/{self.config.BASE_CURRENCY}"
        self.timeout = self.config.REQUEST_TIMEOUT
        
        # Объединяем все поддерживаемые валюты
        self.supported_currencies = {
            currency: "Fiat" for currency in self.config.FIAT_CURRENCIES
        }
        self.supported_currencies.update({
            currency: "Crypto" for currency in self.config.CRYPTO_CURRENCIES
        })
        self.supported_currencies[self.config.BASE_CURRENCY] = "Base"
    
    def get_rates(self) -> Dict[str, float]:
        """Получает актуальные курсы валют"""
        try:
            if not self.api_key:
                print("❌ API ключ не установлен в .env файле")
                return self._get_mock_rates()
        
            print(f"🌐 Запрос к ExchangeRate-API...")
            print(f"🔑 Ключ: {self.api_key[:8]}...{self.api_key[-4:]}")
        
            response = requests.get(self.base_url, timeout=self.timeout)
            print(f"📡 Статус ответа: {response.status_code}")
        
            if response.status_code == 403:
                print("❌ Ошибка 403: Неверный API ключ")
                return self._get_mock_rates()
            elif response.status_code == 429:
                print("❌ Ошибка 429: Превышен лимит запросов")
                return self._get_mock_rates()
            elif response.status_code != 200:
                print(f"❌ HTTP ошибка: {response.status_code}")
                return self._get_mock_rates()
        
            response.raise_for_status()
            data = response.json()
        
            if data.get('result') == 'success':
                rates = data.get('conversion_rates', {})
                print(f"✅ Получено {len(rates)} курсов от API")
                return rates
            else:
                error_type = data.get('error-type', 'Unknown error')
                print(f"❌ API ошибка: {error_type}")
                return self._get_mock_rates()
            
        except requests.RequestException as e:
            print(f"❌ Ошибка сети: {e}")
            return self._get_mock_rates()
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            return self._get_mock_rates()
    
    def _get_mock_rates(self) -> Dict[str, float]:
        """Возвращает тестовые данные для разработки"""
        print("⚠️ Используются тестовые данные")
        return {
            currency: 1.0 if currency == self.config.BASE_CURRENCY else 0.1 * i
            for i, currency in enumerate(self.config.FIAT_CURRENCIES + self.config.CRYPTO_CURRENCIES, 1)
        }# valutatrade_hub/parser_service/api_clients.py
import requests
from typing import Dict, Any

from .config import ParserConfig
from valutatrade_hub.core.exceptions import ApiRequestError


class ExchangeRateAPI:
    """Клиент для работы с ExchangeRate-API"""
    
    def __init__(self):
        self.config = ParserConfig()
        self.base_url = f"{self.config.EXCHANGERATE_API_URL}/{self.config.EXCHANGERATE_API_KEY}/latest/{self.config.BASE_CURRENCY}"
        self.timeout = self.config.REQUEST_TIMEOUT
        
        # Объединяем все поддерживаемые валюты
        self.supported_currencies = {
            currency: "Fiat" for currency in self.config.FIAT_CURRENCIES
        }
        self.supported_currencies.update({
            currency: "Crypto" for currency in self.config.CRYPTO_CURRENCIES
        })
        self.supported_currencies[self.config.BASE_CURRENCY] = "Base"
    
    def get_rates(self) -> Dict[str, float]:
        """
        Получает актуальные курсы валют относительно USD
        """
        try:
            print(f"🌐 Запрос к ExchangeRate-API...")
            
            # Проверяем наличие API ключа
            if not self.config.EXCHANGERATE_API_KEY:
                print("❌ API ключ не установлен. Используются тестовые данные")
                return self._get_mock_rates()
            
            response = requests.get(self.base_url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            if data.get('result') == 'success':
                rates = data.get('conversion_rates', {})
                print(f"✅ Получено {len(rates)} курсов валют от API")
                return rates
            else:
                error_type = data.get('error-type', 'Unknown error')
                print(f"❌ API ошибка: {error_type}")
                return self._get_mock_rates()
            
        except requests.RequestException as e:
            print(f"❌ Ошибка сети: {e}")
            return self._get_mock_rates()
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            return self._get_mock_rates()
    
    def _get_mock_rates(self) -> Dict[str, float]:
        """Возвращает тестовые данные для разработки"""
        print("⚠️ Используются тестовые данные")
        return {
            currency: 1.0 if currency == self.config.BASE_CURRENCY else 0.1 * i
            for i, currency in enumerate(self.config.FIAT_CURRENCIES + self.config.CRYPTO_CURRENCIES, 1)
        }






