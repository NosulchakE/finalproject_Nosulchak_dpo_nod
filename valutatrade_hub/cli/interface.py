# valutatrade_hub/cli/interface.py
import argparse
from datetime import datetime

from valutatrade_hub.core.usecases import (
    register_user,
    login_user,
    show_portfolio,
    buy_currency,
    sell_currency,
    get_rate,
)
from valutatrade_hub.parser_service.updater import RatesUpdater
from valutatrade_hub.core.exceptions import (
    InsufficientFundsError,
    CurrencyNotFoundError,
    ApiRequestError,
)

# Глобальная переменная для текущей сессии
CURRENT_USER = None
def run_interactive_cli():
    """Интерактивный режим CLI"""
    global CURRENT_USER
    
    print("Добро пожаловать в ValutaTrade Hub! Введите 'help' для списка команд.")
    
    while True:
        try:
            if CURRENT_USER:
                prompt = f"\033[92m{CURRENT_USER['username']}>\033[0m "
            else:
                prompt = "guest> "
            
            user_input = input(prompt).strip()
            if not user_input:
                continue
                
            if user_input.lower() in ['exit', 'quit']:
                cmd_exit()
                break
            elif user_input.lower() == 'help':
                print_help()
            else:
                # Парсим команду вручную
                process_command(user_input)
                
        except KeyboardInterrupt:
            print("\nВыход...")
            break
        except Exception as e:
            print(f"Ошибка: {e}")

def print_help():
    """Показать справку по командам"""
    commands = [
        ("register <username> <password>", "Регистрация"),
        ("login <username> <password>", "Вход"),
        ("logout", "Выход"),
        ("show-portfolio [--base USD]", "Портфель"),
        ("buy <currency> <amount>", "Купить валюту"),
        ("sell <currency> <amount>", "Продать валюту"),
        ("get-rate <from> <to>", "Курс валют"),
        ("update-rates", "Обновить курсы"),
        ("exit", "Выход из программы")
    ]
    
    print("\nДоступные команды:")
    for cmd, desc in commands:
        print(f"  {cmd:30} - {desc}")

def process_command(user_input: str):
    """Обработать команду из интерактивного ввода"""
    global CURRENT_USER
    
    parts = user_input.split()
    command = parts[0].lower()
    args = parts[1:]
    
    if command == "register" and len(args) == 2:
        cmd_register_simple(args[0], args[1])
    elif command == "login" and len(args) == 2:
        cmd_login_simple(args[0], args[1])
    elif command == "logout":
        CURRENT_USER = None
        print("Вы вышли из системы")
    elif command == "show-portfolio":
        base = "USD"
        if args and args[0].startswith("--base="):
            base = args[0].split("=")[1]
        cmd_show_portfolio_simple(base)
    elif command == "buy" and len(args) == 2:
        cmd_buy_simple(args[0], float(args[1]))
    elif command == "sell" and len(args) == 2:
        cmd_sell_simple(args[0], float(args[1]))
    elif command == "get-rate" and len(args) == 2:
        cmd_get_rate_simple(args[0], args[1])
    elif command == "update-rates":
        cmd_update_rates_simple()
    else:
        print(f"Неизвестная команда: {command}. Введите 'help' для справки.")


def cmd_register_simple(username: str, password: str):
    try:
        user = register_user(username, password)
        print(f"Пользователь '{user['username']}' зарегистрирован. ID: {user['user_id']}")
    except ValueError as e:
        print(f"Ошибка: {e}")

def cmd_login_simple(username: str, password: str):
    global CURRENT_USER
    try:
        user = login_user(username, password)
        CURRENT_USER = user
        print(f"Вы вошли как '{user['username']}'")
    except ValueError as e:
        print(f"Ошибка: {e}")

def cmd_show_portfolio_simple(base: str = "USD"):
    if not CURRENT_USER:
        print("Сначала выполните login")
        return
    try:
        show_portfolio(CURRENT_USER['user_id'], base_currency=base)
    except CurrencyNotFoundError as e:
        print(e)

def cmd_buy_simple(currency: str, amount: float):
    if not CURRENT_USER:
        print("Сначала выполните login")
        return
    try:
        buy_currency(CURRENT_USER['user_id'], currency, amount)
        print(f"Куплено {amount} {currency}")
    except Exception as e:
        print(f"Ошибка: {e}")

def cmd_sell_simple(currency: str, amount: float):
    if not CURRENT_USER:
        print("Сначала выполните login")
        return
    try:
        sell_currency(CURRENT_USER['user_id'], currency, amount)
        print(f"Продано {amount} {currency}")
    except Exception as e:
        print(f"Ошибка: {e}")

def cmd_get_rate_simple(from_currency: str, to_currency: str):
    try:
        rate, updated_at = get_rate(from_currency, to_currency)
        print(f"Курс {from_currency}→{to_currency}: {rate} (обновлено: {updated_at})")
    except Exception as e:
        print(f"Ошибка: {e}")

def cmd_update_rates_simple():
    try:
        updater = RatesUpdater()
        total = updater.run_update()
        print(f"Обновлено курсов: {total}")
    except Exception as e:
        print(f"Ошибка: {e}")


def run_cli():
    """Главная функция CLI"""
    parser = argparse.ArgumentParser(description="ValutaTrade CLI")
    subparsers = parser.add_subparsers(title="Commands")

    # register
    parser_register = subparsers.add_parser("register", help="Зарегистрировать нового пользователя")
    parser_register.add_argument("--username", required=True)
    parser_register.add_argument("--password", required=True)
    parser_register.set_defaults(func=cmd_register)

    # login
    parser_login = subparsers.add_parser("login", help="Войти в систему")
    parser_login.add_argument("--username", required=True)
    parser_login.add_argument("--password", required=True)
    parser_login.set_defaults(func=cmd_login)

    # show-portfolio
    parser_show = subparsers.add_parser("show-portfolio", help="Показать текущий портфель")
    parser_show.add_argument("--base", default="USD")
    parser_show.set_defaults(func=cmd_show_portfolio)

    # buy
    parser_buy = subparsers.add_parser("buy", help="Купить валюту")
    parser_buy.add_argument("--currency", required=True)
    parser_buy.add_argument("--amount", type=float, required=True)
    parser_buy.set_defaults(func=cmd_buy)

    # sell
    parser_sell = subparsers.add_parser("sell", help="Продать валюту")
    parser_sell.add_argument("--currency", required=True)
    parser_sell.add_argument("--amount", type=float, required=True)
    parser_sell.set_defaults(func=cmd_sell)

    # get-rate
    parser_rate = subparsers.add_parser("get-rate", help="Получить курс валюты")
    parser_rate.add_argument("--from_currency", required=True)
    parser_rate.add_argument("--to_currency", required=True)
    parser_rate.set_defaults(func=cmd_get_rate)

    # update-rates
    parser_update = subparsers.add_parser("update-rates", help="Обновить все курсы валют")
    parser_update.add_argument("--source", default=None)
    parser_update.set_defaults(func=cmd_update_rates)

    # exit
    parser_exit = subparsers.add_parser("exit", help="Выйти из CLI")
    parser_exit.set_defaults(func=cmd_exit)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    run_cli()

















