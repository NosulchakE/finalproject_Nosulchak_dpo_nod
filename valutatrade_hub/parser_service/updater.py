# valutatrade_hub/parser_service/updater.py
import logging
from .api_clients import ExchangeRateApiClient
from .storage import RatesStorage
from .config import ParserConfig

logger = logging.getLogger(__name__)

class RatesUpdater:
    """Основной класс обновления курсов"""

    def __init__(self):
        self.config = ParserConfig()
        self.client = ExchangeRateApiClient(self.config)
        self.storage = RatesStorage(self.config.RATES_FILE_PATH, self.config.HISTORY_FILE_PATH)

    def run_update(self):
        logger.info("Starting rates update...")
        try:
            rates = self.client.fetch_rates()
            logger.info(f"Fetched {len(rates)} rates from ExchangeRate-API")
            self.storage.save_rates(rates)
            self.storage.append_history(rates)
            logger.info("Update successful.")
        except Exception as e:
            logger.error(f"Update failed: {e}")
            raise
