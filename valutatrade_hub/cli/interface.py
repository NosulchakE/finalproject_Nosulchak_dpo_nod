# valutatrade_hub/cli/interface.py
import logging
from getpass import getpass
from valutatrade_hub.core import usecases


# Используем централизованное логирование 
logger = logging.getLogger("CLI")

# Глобальная переменная для текущего пользователя 
CURRENT_USER = None


def run_interactive_cli():
    logger.info("Добро пожаловать в ValutaTrade Hub!")
    logger.info("  7. show_rates      - Показать курсы валют")
    
    # Локальная переменная 
    current_user = None
    
    while True:
        logger.info("\nДоступные команды:")
        logger.info("  1. register         - Регистрация")
        logger.info("  2. login            - Вход")
        logger.info("  3. portfolio        - Показать портфель")
        logger.info("  4. buy              - Купить валюту")
        logger.info("  5. sell             - Продать валюту")
        logger.info("  6. update_rates     - Обновить курсы")
        logger.info("  0. exit             - Выход")

        command = input("\nВведите команду: ").strip().lower()

        try:
            if command in ("1", "register"):
                current_user = _register()
                CURRENT_USER = current_user  # Обновляем глобальную для совместимости
            elif command in ("2", "login"):
                current_user = _login()
                CURRENT_USER = current_user  # Обновляем глобальную для совместимости
            elif command in ("3", "portfolio"):
                _show_portfolio(current_user)
            elif command in ("4", "buy"):
                _buy_currency(current_user)
            elif command in ("5", "sell"):
                _sell_currency(current_user)
            elif command in ("6", "update_rates"):
                _update_rates()
            elif command in ("7", "show_rates"):
                show_rates_command()
            elif command in ("0", "exit"):
                logger.info("Выход из программы...")
                break
            else:
                logger.warning("Неизвестная команда")
        except Exception as e:
            logger.error(f"Ошибка при выполнении команды: {e}")


def _register():
    username = input("Введите имя пользователя: ").strip()
    password = getpass("Введите пароль: ").strip()
    try:
        user = usecases.register_user(username, password)
        logger.info(f"Регистрация успешна. Вы вошли как {username}")
        return user
    except ValueError as e:
        logger.warning(str(e))
        return None


def _login():
    username = input("Введите имя пользователя: ").strip()
    password = getpass("Введите пароль: ").strip()
    try:
        user = usecases.login_user(username, password)
        logger.info(f"Вы вошли как {username}")
        return user
    except ValueError as e:
        logger.warning(str(e))
        return None


def _show_portfolio(current_user):
    if not current_user:
        logger.warning("Команда доступна только для залогиненного пользователя")
        return
    try:
        usecases.show_portfolio(current_user["user_id"])
    except Exception as e:
        logger.error(f"Не удалось показать портфель: {e}")


def _buy_currency(current_user):
    if not current_user:
        logger.warning("Команда доступна только для залогиненного пользователя")
        return
    
    currency = input("Введите валюту для покупки: ").strip().upper()
    amount_str = input("Введите количество: ").strip()
    
    try:
        amount = float(amount_str)
        usecases.buy_currency(current_user["user_id"], currency, amount)
    except ValueError as e:
        logger.warning(f"Ошибка ввода: {e}")
    except Exception as e:
        logger.error(f"Не удалось купить валюту: {e}")


def _sell_currency(current_user):
    if not current_user:
        logger.warning("Команда доступна только для залогиненного пользователя")
        return
    
    currency = input("Введите валюту для продажи: ").strip().upper()
    amount_str = input("Введите количество: ").strip()
    
    try:
        amount = float(amount_str)
        usecases.sell_currency(current_user["user_id"], currency, amount)
    except ValueError as e:
        logger.warning(f"Ошибка ввода: {e}")
    except Exception as e:
        logger.error(f"Не удалось продать валюту: {e}")

# обновление курсов
def _update_rates():
    try:
        updated_count = usecases.update_rates()
        logger.info(f"Обновлено {updated_count} курсов валют")
    except Exception as e:
        logger.error(f"Ошибка при обновлении курсов: {e}")
# показать рейтинг курсов
def show_rates_command():
    """Показать курсы валют"""
    currency = input("Валюта (Enter - все): ").strip().upper()
    currency = currency if currency else None
    
    top_str = input("Топ N криптовалют (Enter - пропустить): ").strip()
    top = int(top_str) if top_str else None
    
    usecases.show_rates(currency=currency, top=top)



























