# valutatrade_hub/decorators.py
import functools
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def log_action(action: str, verbose: bool = False):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            timestamp = datetime.now().isoformat()
            
            try:
                # Берем данные из аргументов
                username = "unknown"
                user_id = "unknown"
                currency_code = ""
                amount = ""
                
                if args:
                    # для buy/sell: (user_id, currency, amount)
                    if action in ("BUY", "SELL") and len(args) >= 3:
                        user_id = args[0]
                        currency_code = args[1]
                        amount = args[2]
                    # Для register/login: (username, password)
                    elif action in ("REGISTER", "LOGIN") and len(args) >= 1:
                        username = args[0]
                
                # Выполняем функцию
                result = func(*args, **kwargs)
                
                # Логируем успех
                log_msg = f"timestamp={timestamp} action={action} username='{username}' user_id={user_id}"
                if currency_code:
                    log_msg += f" currency_code='{currency_code}'"
                if amount:
                    log_msg += f" amount={amount}"
                log_msg += " result=OK"
                
                logger.info(log_msg)
                return result
                
            except Exception as e:
                # Логируем ошибку
                error_msg = f"timestamp={timestamp} action={action} username='{username}' user_id={user_id} result=ERROR error_type={type(e).__name__} error_message='{str(e)}'"
                logger.info(error_msg)
                raise
        
        return wrapper
    return decorator



