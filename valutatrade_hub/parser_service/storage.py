# valutatrade_hub/parser_service/storage.py
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any


class RatesStorage:
    """Класс для работы с историческими данными курсов"""
    
    def __init__(self):
        self.data_file = Path("data/exchange_rates.json")
        self.data_file.parent.mkdir(exist_ok=True)
    
    def save_rates(self, rates: Dict[str, Any]):
        """
        Сохраняет курсы валют с временной меткой
        
        Args:
            rates: Словарь с курсами валют
        """
        # Загружаем существующие данные
        data = self._load_data()
        
        # Добавляем новую запись
        timestamp = datetime.now(timezone.utc).isoformat()
        data[timestamp] = rates
        
        # Сохраняем обратно
        self._save_data(data)
    
    def _load_data(self) -> Dict[str, Any]:
        """Загружает данные из файла"""
        if not self.data_file.exists():
            return {}
        
        with open(self.data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_data(self, data: Dict[str, Any]):
        """Сохраняет данные в файл"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_latest_rates(self) -> Dict[str, Any]:
        """Возвращает последние сохраненные курсы"""
        data = self._load_data()
        if not data:
            return {}
        
        # Берем последнюю временную метку
        latest_timestamp = sorted(data.keys())[-1]
        return data[latest_timestamp]



