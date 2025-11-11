# valutatrade_hub/parser_service/api_clients.py
import requests
from datetime import datetime
from valutatrade_hub.core.exceptions import ApiRequestError
from .config import ParserConfig

class ExchangeRateApiClient:
    """Клиент для ExchangeRate-API"""
    def __init__(self, config: ParserConfig):
        self.config = config

    def fetch_rates(self):
        url = f"{self.config.EXCHANGERATE_API_URL}/{self.config.EXCHANGERATE_API_KEY}/latest/{self.config.BASE_CURRENCY}"
        try:
            response = requests.get(url, timeout=self.config.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            if data.get("result") != "success":
                raise ApiRequestError(f"ExchangeRate-API returned failure: {data}")
            
            rates = {}
            updated_at = datetime.strptime(data["time_last_update_utc"], "%a, %d %b %Y %H:%M:%S +0000").isoformat() + "Z"
            for code, rate in data["rates"].items():
                if code.upper() in self.config.FIAT_CURRENCIES + self.config.CRYPTO_CURRENCIES:
                    key = f"{code.upper()}_{self.config.BASE_CURRENCY}"
                    rates[key] = {
                        "rate": rate,
                        "updated_at": updated_at,
                        "source": "ExchangeRate-API"
                    }
            return rates
        except requests.exceptions.RequestException as e:
            raise ApiRequestError(f"Ошибка при обращении к ExchangeRate-API: {e}") from e
