import functools
from typing import Callable
from valutatrade_hub.logging_config import logger
from valutatrade_hub.core.usecases import get_current_user


def log_action(action: str, verbose: bool = True):
    """
    Декоратор для логирования действий (buy/sell/register/login).
    
    :param action: Название действия (BUY, SELL, REGISTER, LOGIN)
    :param verbose: Включает контекст результата (например, "было->стало")
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            user = None
            try:
                try:
                    user = get_current_user()
                    username = user.username
                    user_id = user.user_id
                except Exception:
                    username = kwargs.get("username", "N/A")
                    user_id = "N/A"

                result = "OK"
                value_before = kwargs.get("value_before", None)

                res = func(*args, **kwargs)

                value_after = res if verbose else None

                log_parts = [
                    f"action={action}",
                    f"user='{username}'",
                ]

                if "currency_code" in kwargs:
                    log_parts.append(f"currency='{kwargs['currency_code']}'")
                if "amount" in kwargs:
                    log_parts.append(f"amount={kwargs['amount']}")
                if "rate" in kwargs:
                    log_parts.append(f"rate={kwargs['rate']}")
                if "base" in kwargs:
                    log_parts.append(f"base='{kwargs['base']}'")

                log_parts.append(f"result={result}")
                if verbose and value_before is not None and value_after is not None:
                    log_parts.append(f"context='{value_before}→{value_after}'")

                logger.info(" ".join(log_parts))
                return res

            except Exception as e:
                error_type = type(e).__name__
                error_message = str(e)
                log_parts = [
                    f"action={action}",
                    f"user='{username}'",
                    "result=ERROR",
                    f"error_type={error_type}",
                    f"error_message='{error_message}'"
                ]
                logger.info(" ".join(log_parts))
                raise  # проброс исключения дальше

        return wrapper
    return decorator
