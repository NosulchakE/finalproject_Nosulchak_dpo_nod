# valutatrade_hub/parser_service/api_clients.py
import os
import requests
from typing import Dict, Any

from valutatrade_hub.infra.settings import SettingsLoader
from valutatrade_hub.core.exceptions import ApiRequestError


class ExchangeRateAPI:
    """Клиент для работы с ExchangeRate-API"""
    
    def __init__(self):
        self.settings = SettingsLoader()
        self.api_key = self.settings.EXCHANGERATE_API_KEY
        self.base_url = "https://api.exchangerate-api.com/v4/latest/USD"
        self.timeout = self.settings.REQUEST_TIMEOUT
        
        # Список поддерживаемых валют
        self.supported_currencies = {
            "EUR": "Euro",
            "GBP": "British Pound", 
            "JPY": "Japanese Yen",
            "CAD": "Canadian Dollar",
            "CHF": "Swiss Franc",
            "AUD": "Australian Dollar",
            "CNY": "Chinese Yuan",
            "BTC": "Bitcoin",
            "ETH": "Ethereum",
            "RUB": "Russian Ruble",
        }
    
    def get_rates(self) -> Dict[str, float]:
        """
        Получает актуальные курсы валют относительно USD
        
        Returns:
            Dict[str, float]: Словарь с курсами валют
        """
        try:
            print(f"🌐 Запрос к ExchangeRate-API...")
            
            # В реальной реализации здесь будет запрос к API
            # response = requests.get(self.base_url, timeout=self.timeout)
            # response.raise_for_status()
            # data = response.json()
            # return data.get('rates', {})
            
            # ЗАГЛУШКА: возвращаем тестовые данные
            print("⚠️ Используются тестовые данные (API отключено)")
            return self._get_mock_rates()
            
        except requests.RequestException as e:
            print(f"❌ Ошибка сети: {e}")
            # Возвращаем тестовые данные при ошибке
            return self._get_mock_rates()
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            return self._get_mock_rates()
    
    def _get_mock_rates(self) -> Dict[str, float]:
        """Возвращает тестовые данные для разработки"""
        return {
            "EUR": 0.92,
            "GBP": 0.79, 
            "JPY": 149.50,
            "CAD": 1.36,
            "CHF": 0.88,
            "AUD": 1.52,
            "CNY": 7.25,
            "RUB": 92.50,
            "BTC": 0.000016,  # 1 USD в BTC
            "ETH": 0.00027,   # 1 USD в ETH
        }


