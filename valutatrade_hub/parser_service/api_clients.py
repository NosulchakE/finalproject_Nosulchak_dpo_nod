import requests
from .config import ParserConfig
from valutatrade_hub.core.exceptions import ApiRequestError

class ExchangeRateApiClient:
    def __init__(self, config: ParserConfig):
        self.config = config

    def fetch_rates(self):
        url = f"{self.config.EXCHANGERATE_API_URL}/{self.config.EXCHANGERATE_API_KEY}/latest/{self.config.BASE_CURRENCY}"
        try:
            resp = requests.get(url, timeout=self.config.REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            if data.get("result") != "success":
                raise ApiRequestError(f"ExchangeRate-API error: {data}")
            
            rates = {}
            updated_at = data.get("time_last_update_utc")
            for code in self.config.FIAT_CURRENCIES + self.config.CRYPTO_CURRENCIES:
                if code not in data["rates"]:
                    continue
                rates[f"{code}_USD"] = {
                    "rate": data["rates"][code],
                    "updated_at": updated_at,
                    "source": "ExchangeRate-API"
                }
            return rates

        except requests.RequestException as e:
            raise ApiRequestError(f"Network error: {e}")


