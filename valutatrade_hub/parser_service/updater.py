# valutatrade_hub/parser_service/updater.py
from .api_clients import ExchangeRateAPI, CoinGeckoAPI
from datetime import datetime, timezone
from typing import Dict, Any
import logging

from .storage import RatesStorage
from .config import ParserConfig
from valutatrade_hub.core.exceptions import ApiRequestError
from valutatrade_hub.infra.database import JSONDatabase  

logger = logging.getLogger(__name__)


class RatesUpdater:
    """Класс для обновления курсов валют"""

    def __init__(self, source: str = None):
        self.config = ParserConfig()
        self.source = source or "combined"
        self.fiat_api = ExchangeRateAPI()
        self.crypto_api = CoinGeckoAPI()
        self.storage = RatesStorage()
        self.db = JSONDatabase()

    def run_update(self) -> int:
        try:
            logger.info("Обновление курсов валют...")
        
            fiat_rates = self.fiat_api.get_rates()
            crypto_rates = self.crypto_api.get_rates()
            logger.info(f"Курсы крипты: {crypto_rates}")  # Временно!!!! тестим ошибку курса
        
            all_rates = {**fiat_rates, **crypto_rates}
        
            if not all_rates:
                logger.warning("Нет данных от API")
                return 0
        
            updated_count = self._update_rates_cache(all_rates)
            self._save_historical_data(all_rates)
        
            logger.info(f"Обновлено {updated_count} курсов")
            return updated_count
        
        except Exception as e:
            logger.error(f"Ошибка обновления: {e}")
            raise ApiRequestError(f"Ошибка API: {e}")

    def _update_rates_cache(self, fresh_rates: Dict[str, Any]) -> int:
        """
        Обновляет rates.json через общую базу данных
        """
        rates_data = {
            "pairs": {},
            "last_refresh": datetime.now(timezone.utc).isoformat()
        }

        updated_count = 0
        base_currency = self.config.BASE_CURRENCY

        # применяем фильтр, оставляем только нужные валюты
        target_currencies = set(self.config.FIAT_CURRENCIES + self.config.CRYPTO_CURRENCIES)

        for currency, rate in fresh_rates.items():
            if currency in target_currencies and currency != base_currency:
                # формируем пару: BASE - Currency
                pair_key = f"{base_currency}_{currency}"
                rates_data["pairs"][pair_key] = {
                    "rate": rate,
                    "updated_at": rates_data["last_refresh"],
                    "source": self.source
                }
                updated_count += 1

                # Обратная пара: Currency - BASE
                if rate != 0:
                    pair_key = f"{currency}_{base_currency}"
                    rates_data["pairs"][pair_key] = {
                        "rate": 1 / rate,
                        "updated_at": rates_data["last_refresh"],
                        "source": self.source
                    }
                    updated_count += 1

        # Сохраняем 
        try:
            self.db.save_rates(rates_data)
            logger.debug("Локальный кэш обновлен")
        except Exception as e:
            logger.error(f"Не удалось сохранить rates.json: {e}")

        return updated_count

    def _save_historical_data(self, fresh_rates: Dict[str, Any]):
        """Сохраняет исторические данные через storage"""
        try:
            self.storage.save_rates(fresh_rates)
            logger.debug("исторические данные успешно сохранены")
        except Exception as e:
            logger.warning(f"Не удалось сохранить исторические данные: {e}")













