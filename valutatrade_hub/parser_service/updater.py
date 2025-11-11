from .config import ParserConfig
from .api_clients import ExchangeRateApiClient
from .storage import RatesStorage
import logging

logger = logging.getLogger("parser_service")
logging.basicConfig(level=logging.INFO)

class RatesUpdater:
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
            logger.info("Rates saved successfully")
        except Exception as e:
            logger.error(f"Update failed: {e}")


