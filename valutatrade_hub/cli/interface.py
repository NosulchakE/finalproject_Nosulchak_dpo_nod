# valutatrade_hub/cli/interface.py
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


def cmd_register_simple(username: str, password: str):
    """Регистрация пользователя (упрощенная версия)"""
    try:
        user = register_user(username, password)
        print(f"Пользователь '{user['username']}' зарегистрирован. ID: {user['user_id']}")
    except ValueError as e:
        print(f"Ошибка: {e}")


def cmd_login_simple(username: str, password: str):
    """Авторизация пользователя (упрощенная версия)"""
    global CURRENT_USER
    try:
        user = login_user(username, password)
        CURRENT_USER = user
        print(f"Вы вошли как '{user['username']}'!")
    except ValueError as e:
        print(f"Ошибка: {e}")


def cmd_show_portfolio_simple(base: str = "USD"):
    """Показать портфель пользователя (упрощенная версия)"""
    if not CURRENT_USER:
        print("Сначала выполните login")
        return
    try:
        show_portfolio(CURRENT_USER['user_id'], base_currency=base)
    except CurrencyNotFoundError as e:
        print(e)


def cmd_buy_simple(currency: str, amount: float):
    """Покупка валюты (упрощенная версия)"""
    if not CURRENT_USER:
        print("Сначала выполните login")
        return
    try:
        buy_currency(CURRENT_USER['user_id'], currency, amount)
    except (ValueError, CurrencyNotFoundError, ApiRequestError, InsufficientFundsError) as e:
        print(f"Ошибка: {e}")


def cmd_sell_simple(currency: str, amount: float):
    """Продажа валюты (упрощенная версия)"""
    if not CURRENT_USER:
        print("Сначала выполните login")
        return
    try:
        sell_currency(CURRENT_USER['user_id'], currency, amount)
    except (InsufficientFundsError, ValueError, CurrencyNotFoundError, ApiRequestError) as e:
        print(f"Ошибка: {e}")


def cmd_get_rate_simple(from_currency: str, to_currency: str):
    """Получить курс валюты (упрощенная версия)"""
    try:
        rate, updated_at = get_rate(from_currency, to_currency)
        print(f"Курс {from_currency}→{to_currency}: {rate} (обновлено: {updated_at})")
    except CurrencyNotFoundError as e:
        print(f"Ошибка: {e}")
    except ApiRequestError as e:
        print(f"Ошибка API: {e}")


def cmd_update_rates_simple():
    """Обновить курсы валют (упрощенная версия)"""
    try:
        updater = RatesUpdater()
        total = updater.run_update()
        print(f"Обновлено курсов: {total}")
    except ApiRequestError as e:
        print(f"Ошибка API: {e}")


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
    if not parts:
        return
        
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
        elif args and args[0] == "--base" and len(args) > 1:
            base = args[1]
        cmd_show_portfolio_simple(base)
    elif command == "buy" and len(args) == 2:
        try:
            amount = float(args[1])
            cmd_buy_simple(args[0], amount)
        except ValueError:
            print("Ошибка: количество должно быть числом")
    elif command == "sell" and len(args) == 2:
        try:
            amount = float(args[1])
            cmd_sell_simple(args[0], amount)
        except ValueError:
            print("Ошибка: количество должно быть числом")
    elif command == "get-rate" and len(args) == 2:
        cmd_get_rate_simple(args[0], args[1])
    elif command == "update-rates":
        cmd_update_rates_simple()
    else:
        print(f"Неизвестная команда: {command}. Введите 'help' для справки.")


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
                
            # Обрабатываем команды выхода
            if user_input.lower() in ['exit', 'quit']:
                print("Выход из ValutaTrade Hub...")
                break
            elif user_input.lower() == 'help':
                print_help()
            else:
                process_command(user_input)
                
        except KeyboardInterrupt:
            print("\nВыход...")
            break
        except EOFError:  # Обработка Ctrl+D
            print("\nВыход...")
            break
        except Exception as e:
            print(f"Ошибка: {e}")





















