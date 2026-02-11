# valutatrade_hub/decorators.py
import functools
from typing import Callable
from datetime import datetime
import logging

logger = logging.getLogger("valutatrade.actions")

def log_action(action: str, verbose: bool = False):
    """
    Декоратор для логирования действий (buy/sell/register/login).
    
    :param action: Название действия (BUY, SELL, REGISTER, LOGIN)
    :param verbose: Включает контекст результата (например, "было->стало") (требование ТЗ!!)
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Собираем данные для лога
            log_data = {
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "username": "unknown",
                "user_id": "unknown",
                "result": "OK"
            }
            
            try:
                # Извлекаем информацию из аргументов
                # Для register/login: args = (username, password)
                # Для buy/sell: args = (user_id, currency, amount)
                
                if len(args) >= 1:
                    # Первый аргумент - user_id для buy/sell или username для register
                    if isinstance(args[0], int):
                        log_data["user_id"] = args[0]
                    elif isinstance(args[0], str):
                        log_data["username"] = args[0]
                
                # Второй аргумент - currency для buy/sell или password для register
                if len(args) >= 2 and isinstance(args[1], str):
                    if action in ("BUY", "SELL"):
                        log_data["currency_code"] = args[1]
                
                # Третий аргумент - amount для buy/sell
                if len(args) >= 3:
                    if action in ("BUY", "SELL"):
                        log_data["amount"] = args[2]
                
                # Выполняем функцию
                result = func(*args, **kwargs)
                
                # Логируем успех
                _log_action(log_data)
                return result
                
            except Exception as e:
                # Логируем ошибку
                log_data["result"] = "ERROR"
                log_data["error_type"] = type(e).__name__
                log_data["error_message"] = str(e)
                
                _log_action(log_data)
                raise  # пробрасываем исключение дальше
        
        return wrapper
    return decorator


def _log_action(log_data: dict):
    """Вспомогательная функция для логирования в формате строки"""
    parts = []
    
    # Обязательные поля
    parts.append(f"timestamp={log_data['timestamp']}")
    parts.append(f"action={log_data['action']}")
    parts.append(f"username='{log_data['username']}'")
    parts.append(f"user_id={log_data['user_id']}")
    
    # опциональные поля
    if "currency_code" in log_data:
        parts.append(f"currency_code='{log_data['currency_code']}'")
    if "amount" in log_data:
        parts.append(f"amount={log_data['amount']}")
    if "rate" in log_data:
        parts.append(f"rate={log_data['rate']}")
    if "base" in log_data:
        parts.append(f"base='{log_data['base']}'")
    
    # Результат
    parts.append(f"result={log_data['result']}")
    
    # Ошибки если есть
    if log_data["result"] == "ERROR":
        parts.append(f"error_type={log_data['error_type']}")
        parts.append(f"error_message='{log_data['error_message']}'")
    
    # Контекст для verbose режима
    if "context_before" in log_data and "context_after" in log_data:
        parts.append(f"context='{log_data['context_before']}→{log_data['context_after']}'")
    
    logger.info(" ".join(parts))


