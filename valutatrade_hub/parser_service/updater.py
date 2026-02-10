# valutatrade_hub/parser_service/updater.py
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

from .api_clients import BaseApiClient, ExchangeRateApiClient
from .storage import RatesStorage
from .config import ParserConfig
from valutatrade_hub.core.exceptions import ApiRequestError


class RatesUpdater:
    """Класс для обновления курсов валют"""
    
    def __init__(self, source: str = None):
        self.config = ParserConfig()
        self.source = source or "exchangerate-api"
        self.api_client: BaseApiClient = ExchangeRateApiClient()
        self.storage = RatesStorage()
        
    def run_update(self) -> int:
        """Основной метод обновления курсов"""
        print(f"обновление курсов валют из {self.source}...")
        try:
            fresh_rates = self.api_client.fetch_rates()
        except ApiRequestError as e:
            print(f" Ошибка API ({self.source}): {e}. Используем тестовые данные")
            fresh_rates = self.api_client.fetch_rates()  # заглушка внутри клиента в случае некорректной работы  API

        if not fresh_rates:
            print(" Не получены данные от API и заглушка пустая")
            return 0
        
        updated_count = self._update_rates_cache(fresh_rates)
        self._save_historical_data(fresh_rates)
        
        print(f" обновлено {updated_count} курсов валют")
        return updated_count
    
    def _update_rates_cache(self, fresh_rates: Dict[str, Any]) -> int:
        """Обновляет файл rates.json (локальный кэш для Core Service)"""
        rates_file = Path(self.config.RATES_FILE_PATH)
        rates_file.parent.mkdir(parents=True, exist_ok=True)
        
        base_currency = self.config.BASE_CURRENCY
        target_currencies = set(self.config.FIAT_CURRENCIES + self.config.CRYPTO_CURRENCIES)
        last_refresh = datetime.now(timezone.utc).isoformat()
        
        pairs = {}
        updated_count = 0

        for currency, rate in fresh_rates.items():
            if currency in target_currencies and currency != base_currency:
                pairs[f"{base_currency}_{currency}"] = {"rate": rate, "updated_at": last_refresh, "source": self.source}
                updated_count += 1
                if rate != 0:
                    pairs[f"{currency}_{base_currency}"] = {"rate": 1 / rate, "updated_at": last_refresh, "source": self.source}
                    updated_count += 1
        
        rates_data = {"pairs": pairs, "last_refresh": last_refresh}
        with open(rates_file, 'w', encoding='utf-8') as f:
            json.dump(rates_data, f, ensure_ascii=False, indent=2)
        
        return updated_count
    
    def _save_historical_data(self, fresh_rates: Dict[str, Any]):
        """Сохраняет исторические данные в exchange_rates.json"""
        try:
            self.storage.save_rates(fresh_rates)
        except Exception as e:
            print(f" Не удалось сохранить исторические данные: {e}")








