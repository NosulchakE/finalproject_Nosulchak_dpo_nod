from .config import ParserConfig
from .api_clients import ExchangeRateApiClient
from .storage import RatesStorage
import logging
from valutatrade_hub.core.usecases import update_rates


class RatesUpdater:
    def __init__(self, source: str = None):
        self.source = source

    def run_update(self) -> int:
        try:
            total = update_rates(source=self.source)
            print(f"INFO: Updated {total} rates from source {self.source or 'all'}")
            return total
        except Exception as e:
            print(f"ERROR: Failed to update rates: {e}")
            return 0



