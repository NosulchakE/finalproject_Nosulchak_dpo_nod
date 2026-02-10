# valutatrade_hub/parser_service/updater.py
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any
import logging

from .api_clients import ExchangeRateAPI
from .storage import RatesStorage
from .config import ParserConfig
from valutatrade_hub.core.exceptions import ApiRequestError

# настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


class RatesUpdater:
    """Класс для обновления курсов валют"""

    def __init__(self, source: str = None):
        self.config = ParserConfig()
        self.source = source or "exchangerate-api"
        self.api_client = ExchangeRateAPI()
        self.storage = RatesStorage()

    def run_update(self) -> int:
        """Основной метод обновления курсов"""
        try:
            logger.info(f" Обновление курсов валют из {self.source}...")

            # Получаем свежие курсы от API
            fresh_rates = self.api_client.get_rates()

            if not fresh_rates:
                logger.warning(" Не получены данные от API. Используются тестовые данные")
                return 0

            # Обновляем базу rates.json
            updated_count = self._update_rates_cache(fresh_rates)

            # Сохраняем исторические данные exchange_rates.json
            self._save_historical_data(fresh_rates)

            logger.info(f"  Обновлено {updated_count} курсов валют")
            return updated_count

        except Exception as e:
            logger.error(f"  Ошибка при обновлении курсов: {e}")
            raise ApiRequestError(f"Ошибка API: {e}")

    def _update_rates_cache(self, fresh_rates: Dict[str, Any]) -> int:
        """
        Обновляет файл rates.json 
        """
        rates_file = Path(self.config.RATES_FILE_PATH)
        rates_file.parent.mkdir(exist_ok=True)

        rates_data = {
            "pairs": {},
            "last_refresh": datetime.now(timezone.utc).isoformat()
        }

        updated_count = 0
        base_currency = self.config.BASE_CURRENCY

        # применям фильтр, оставляем только нужные валюты
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

        # Сохраняем полученную информацию в файл
        try:
            with open(rates_file, 'w', encoding='utf-8') as f:
                json.dump(rates_data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Локальный кэш обновлен: {rates_file}")
        except Exception as e:
            logger.error(f"Не удалось сохранить rates.json: {e}")

        return updated_count

    def _save_historical_data(self, fresh_rates: Dict[str, Any]):
        """Сохраняет исторические данные в exchange_rates.json"""
        try:
            self.storage.save_rates(fresh_rates)
            logger.debug("Исторические данные успешно сохранены")
        except Exception as e:
            logger.warning(f"Не удалось сохранить исторические данные: {e}")









