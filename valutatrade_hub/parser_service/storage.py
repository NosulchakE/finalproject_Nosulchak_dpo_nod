# valutatrade_hub/parser_service/storage.py
import json
import os
from datetime import datetime

class RatesStorage:
    """Чтение и запись локального кэша и истории"""

    def __init__(self, rates_file, history_file):
        self.rates_file = rates_file
        self.history_file = history_file
        os.makedirs(os.path.dirname(rates_file), exist_ok=True)
        os.makedirs(os.path.dirname(history_file), exist_ok=True)

    def save_rates(self, rates: dict):
        """Сохранить последний снимок в rates.json"""
        snapshot = {"pairs": rates, "last_refresh": datetime.utcnow().isoformat() + "Z"}
        tmp_file = self.rates_file + ".tmp"
        with open(tmp_file, "w") as f:
            json.dump(snapshot, f, indent=2)
        os.replace(tmp_file, self.rates_file)

    def append_history(self, rates: dict):
        """Добавить записи в exchange_rates.json"""
        history = []
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                try:
                    history = json.load(f)
                except json.JSONDecodeError:
                    history = []

        for key, info in rates.items():
            from_currency, to_currency = key.split("_")
            record = {
                "id": f"{from_currency}_{to_currency}_{info['updated_at']}",
                "from_currency": from_currency,
                "to_currency": to_currency,
                "rate": info["rate"],
                "timestamp": info["updated_at"],
                "source": info["source"],
                "meta": {}
            }
            history.append(record)

        tmp_file = self.history_file + ".tmp"
        with open(tmp_file, "w") as f:
            json.dump(history, f, indent=2)
        os.replace(tmp_file, self.history_file)
