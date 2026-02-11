# valutatrade_hub/parser_service/api_clients.py
import requests
from typing import Dict
import logging

from .config import ParserConfig
from valutatrade_hub.core.exceptions import ApiRequestError

# Используем централизованное логирование
logger = logging.getLogger(__name__)


class ExchangeRateAPI:
    """Клиент для работы с ExchangeRate-API"""

    def __init__(self):
        self.config = ParserConfig()
        self.base_url = f"{self.config.EXCHANGERATE_API_URL}/{self.config.EXCHANGERATE_API_KEY}/latest/{self.config.BASE_CURRENCY}"
        self.timeout = self.config.REQUEST_TIMEOUT

        # Объединяем все поддерживаемые валюты
        self.supported_currencies = {currency: "Fiat" for currency in self.config.FIAT_CURRENCIES}
        self.supported_currencies.update({currency: "Crypto" for currency in self.config.CRYPTO_CURRENCIES})
        self.supported_currencies[self.config.BASE_CURRENCY] = "Base"

    def get_rates(self) -> Dict[str, float]:
        """
        Получение актуальных курсов валют относительно базовой валюты (в соответствии с ТЗ)
        """
        try:
            if not self.config.EXCHANGERATE_API_KEY:
                logger.warning("API ключ не установлен. используются тестовые данные")
                return self._get_mock_rates()

            logger.info("Запрос к ExchangeRate-API...")

            response = requests.get(self.base_url, timeout=self.timeout)
            if response.status_code == 403:
                logger.warning("Ошибка 403: Неверный API ключ. Используются тестовые данные")
                return self._get_mock_rates()
            elif response.status_code == 429:
                logger.warning("Ошибка 429: Превышен лимит запросов. Используются тестовые данные")
                return self._get_mock_rates()
            elif response.status_code != 200:
                logger.warning(f"HTTP ошибка {response.status_code}. Используются тестовые данные")
                return self._get_mock_rates()

            response.raise_for_status()
            data = response.json()

            if data.get("result") == "success":
                rates = data.get("conversion_rates", {})
                logger.info(f"Получено {len(rates)} курсов валют от API")
                return rates
            else:
                error_type = data.get("error-type", "Unknown error")
                logger.warning(f"API ошибка: {error_type}. Используются тестовые данные")
                return self._get_mock_rates()

        except requests.RequestException as e:
            logger.error(f"Ошибка сети при запросе API: {e}. Используются тестовые данные")
            return self._get_mock_rates()
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}. Используются тестовые данные")
            return self._get_mock_rates()

    def _get_mock_rates(self) -> Dict[str, float]:
        """
        Возвращает тестовые данные для разработки
        """
        logger.info("Используются тестовые данные для валют")
        return {
            currency: 1.0 if currency == self.config.BASE_CURRENCY else 0.1 * i
            for i, currency in enumerate(self.config.FIAT_CURRENCIES + self.config.CRYPTO_CURRENCIES, 1)
        }






