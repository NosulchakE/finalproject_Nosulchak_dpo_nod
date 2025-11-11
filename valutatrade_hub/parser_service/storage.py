import json
import os

class RatesStorage:
    def __init__(self, rates_file: str, history_file: str):
        self.rates_file = rates_file
        self.history_file = history_file

    def save_rates(self, rates: dict):
        # Обновление rates.json (текущий снимок)
        snapshot = {"pairs": rates, "last_refresh": max(r["updated_at"] for r in rates.values())}
        with open(self.rates_file, "w") as f:
            json.dump(snapshot, f, indent=2)
        
        # Добавление в exchange_rates.json (история)
        history = []
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                try:
                    history = json.load(f)
                except json.JSONDecodeError:
                    history = []
        for code, val in rates.items():
            entry = {
                "id": f"{code}_{val['updated_at'].replace(':','')}",
                "from_currency": code.split("_")[0],
                "to_currency": code.split("_")[1],
                "rate": val["rate"],
                "timestamp": val["updated_at"],
                "source": val["source"]
            }
            history.append(entry)
        with open(self.history_file, "w") as f:
            json.dump(history, f, indent=2)


