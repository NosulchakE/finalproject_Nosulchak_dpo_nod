# valutatrade_hub/parser_service/storage.py
from datetime import datetime, timezone
from typing import Dict, Any
from valutatrade_hub.infra.database import JSONDatabase  


class RatesStorage:
    """Класс для работы с историческими данными курсов"""
    
    def __init__(self):
        self.db = JSONDatabase()  # ИСПОЛЬЗУЕМ ОБЩУЮ БАЗУ для разделение слоев
    
    def save_rates(self, rates: Dict[str, Any]):
        """
        Сохраняем курсы валют с временной меткой
        """
        # Загружаем исторические данные через общую базу
        historical_data = self.db.load_exchange_rates()
        
        # Добавляем новую запись
        timestamp = datetime.now(timezone.utc).isoformat()
        historical_data[timestamp] = rates
        
        # Сохраняем через общую базу
        self.db.save_exchange_rates(historical_data)
    
    def get_latest_rates(self) -> Dict[str, Any]:
        """Возвращаем последние сохраненные курсы"""
        historical_data = self.db.load_exchange_rates()
        
        if not historical_data:
            return {}
        
        # Находим последнюю временную метку
        timestamps = [ts for ts in historical_data.keys() 
                     if ts not in ["rates", "last_update"]]  # Игнорируем служебные поля ненужные
        
        if not timestamps:
            return {}
        
        latest_timestamp = sorted(timestamps)[-1]
        return historical_data[latest_timestamp]




