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


def cmd_register(args):
    """Регистрация пользователя"""
    try:
        user = register_user(args.username, args.password)
        print(
            f"Пользователь '{user.username}' зарегистрирован (id={user.user_id}). "
            f"Войдите: login --username {user.username} --password ****"
        )
    except ValueError as e:
        print(f"Ошибка: {e}")


def cmd_login(args):
    """Авторизация пользователя"""
    global CURRENT_USER
    try:
        user = login_user(args.username, args.password)
        CURRENT_USER = user
        print(f"Вы вошли как '{user.username}'")
    except ValueError as e:
        print(f"Ошибка: {e}")


def cmd_show_portfolio(args):
    """Показать портфель пользователя"""
    if not CURRENT_USER:
        print("Сначала выполните login")
        return
    try:
        show_portfolio(CURRENT_USER.user_id, base_currency=args.base)
    except CurrencyNotFoundError as e:
        print(f"Ошибка: {e}")


def cmd_buy(args):
    """Покупка валюты"""
    if not CURRENT_USER:
        print("Сначала выполните login")
        return
    try:
        buy_currency(CURRENT_USER.user_id, args.currency, args.amount)
    except (ValueError, CurrencyNotFoundError, ApiRequestError) as e:
        print(f"Ошибка: {e}")


def cmd_sell(args):
    """Продажа валюты"""
    if not CURRENT_USER:
        print("Сначала выполните login")
        return
    try:
        sell_currency(CURRENT_USER.user_id, args.currency, args.amount)
    except (InsufficientFundsError, ValueError, CurrencyNotFoundError, ApiRequestError) as e:
        print(f"Ошибка: {e}")


def cmd_get_rate(args):
    """Получить курс валюты"""
    try:
        rate, updated_at = get_rate(args.from_currency, args.to_currency)
        print(f"Курс {args.from_currency}→{args.to_currency}: {rate} (обновлено: {updated_at})")
    except CurrencyNotFoundError as e:
        print(f"Ошибка: {e}")
    except ApiRequestError as e:
        print(f"Ошибка API: {e}")


def cmd_update_rates(args):
    """Обновить курсы валют"""
    try:
        updater = RatesUpdater(source=args.source)
        total = updater.run_update()
        if total > 0:
            print(f"Update successful. Total rates updated: {total}")
        else:
            print("Update completed, но данных не обновлено")
    except ApiRequestError as e:
        print(f"Ошибка API: {e}")


def cmd_exit(args=None):
    """Выйти из CLI"""
    print("Выход...")
    exit(0)


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














