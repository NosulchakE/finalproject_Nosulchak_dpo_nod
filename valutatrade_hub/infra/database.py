# valutatrade_hub/infra/database.py
import json
import os
from typing import Any, Dict, List

class JSONDatabase:
    """Класс для работы с JSON файлами (инфраструктурный слой)"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def _load_json(self, filename: str, default: Any = None) -> Any:
        """Загрузить данные из JSON файла"""
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            return default if default is not None else {}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # Если файл поврежден, возвращаем значение по умолчанию
            return default if default is not None else {}
    
    def _save_json(self, filename: str, data: Any) -> None:
        """Сохранить данные в JSON файл"""
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Ошибка сохранения {filename}: {e}")
    
    # методы для конкретных файлов
    
    def load_users(self) -> List[Dict]:
        """Загрузить список пользователей"""
        return self._load_json("users.json", [])
    
    def save_users(self, users: List[Dict]) -> None:
        """Сохранить список пользователей"""
        self._save_json("users.json", users)
    
    def load_portfolios(self) -> List[Dict]:
        """загрузить список портфелей"""
        return self._load_json("portfolios.json", [])
    
    def save_portfolios(self, portfolios: List[Dict]) -> None:
        """Сохранить список портфелей"""
        self._save_json("portfolios.json", portfolios)
    
    def load_rates(self) -> Dict:
        """Загрузить курсы валют"""
        return self._load_json("rates.json", {"pairs": {}, "last_refresh": None})
    
    def save_rates(self, rates: Dict) -> None:
        """Сохранить курсы валют"""
        self._save_json("rates.json", rates)
    
    def load_exchange_rates(self) -> Dict:
        """Загрузить исторические курсы валют"""
        return self._load_json("exchange_rates.json", {})
    
    def save_exchange_rates(self, exchange_rates: Dict) -> None:
        """Сохранить исторические курсы валют"""
        self._save_json("exchange_rates.json", exchange_rates)
