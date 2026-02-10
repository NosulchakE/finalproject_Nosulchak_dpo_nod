# valutatrade_hub/cli/interface.py
import logging
from getpass import getpass
from valutatrade_hub.core import usecases

# Настройка логирования для CLI
logger = logging.getLogger("CLI")
logger.setLevel(logging.INFO)
logger.propagate = False  # предотвращаем дублирование сообщений

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Глобальная переменная для текущего пользователя
CURRENT_USER = None

def run_interactive_cli():
    logger.info("Добро пожаловать в ValutaTrade Hub!")
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
                register()
            elif command in ("2", "login"):
                login()
            elif command in ("3", "portfolio"):
                show_portfolio()
            elif command in ("4", "buy"):
                buy_currency()
            elif command in ("5", "sell"):
                sell_currency()
            elif command in ("6", "update_rates"):
                update_rates()
            elif command in ("0", "exit"):
                logger.info("Выход из программы...")
                break
            else:
                logger.warning("Неизвестная команда")
        except Exception as e:
            logger.error(f"Ошибка при выполнении команды: {e}")


def register():
    global CURRENT_USER
    username = input("Введите имя пользователя: ").strip()
    password = getpass("Введите пароль: ").strip()
    try:
        user = usecases.register_user(username, password)
        CURRENT_USER = user
        logger.info(f"Регистрация успешна. Вы вошли как {username}")
    except ValueError as e:
        logger.warning(str(e))


def login():
    global CURRENT_USER
    username = input("Введите имя пользователя: ").strip()
    password = getpass("Введите пароль: ").strip()
    try:
        user = usecases.login_user(username, password)
        CURRENT_USER = user
        logger.info(f"Вы вошли как {username}")
    except ValueError as e:
        logger.warning(str(e))


def show_portfolio():
    if not CURRENT_USER:
        logger.warning("Команда доступна только для залогиненного пользователя")
        return
    try:
        usecases.show_portfolio(CURRENT_USER["user_id"])
    except Exception as e:
        logger.error(f"Не удалось показать портфель: {e}")


def buy_currency():
    if not CURRENT_USER:
        logger.warning("Команда доступна только для залогиненного пользователя")
        return
    currency = input("Введите валюту для покупки: ").strip().upper()
    amount_str = input("Введите количество: ").strip()
    try:
        amount = float(amount_str)
        usecases.buy_currency(CURRENT_USER["user_id"], currency, amount)
    except ValueError as e:
        logger.warning(f"Ошибка ввода: {e}")
    except Exception as e:
        logger.error(f"Не удалось купить валюту: {e}")


def sell_currency():
    if not CURRENT_USER:
        logger.warning("Команда доступна только для залогиненного пользователя")
        return
    currency = input("Введите валюту для продажи: ").strip().upper()
    amount_str = input("Введите количество: ").strip()
    try:
        amount = float(amount_str)
        usecases.sell_currency(CURRENT_USER["user_id"], currency, amount)
    except ValueError as e:
        logger.warning(f"Ошибка ввода: {e}")
    except Exception as e:
        logger.error(f"Не удалось продать валюту: {e}")


def update_rates():
    try:
        updated_count = usecases.update_rates()
        logger.info(f"Обновлено {updated_count} курсов валют")
    except Exception as e:
        logger.error(f"Ошибка при обновлении курсов: {e}")


























