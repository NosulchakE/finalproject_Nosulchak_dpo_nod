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
    update_rates,
    show_rates
)
from valutatrade_hub.core.exceptions import (
    InsufficientFundsError,
    CurrencyNotFoundError,
    ApiRequestError
)

# Простое хранение текущей сессии
CURRENT_USER = {"user_id": None, "username": None}


def main():
    parser = argparse.ArgumentParser(description="ValutaTrade CLI")
    subparsers = parser.add_subparsers(dest="command")

    # register
    reg_parser = subparsers.add_parser("register")
    reg_parser.add_argument("--username", required=True)
    reg_parser.add_argument("--password", required=True)

    # login
    login_parser = subparsers.add_parser("login")
    login_parser.add_argument("--username", required=True)
    login_parser.add_argument("--password", required=True)

    # show-portfolio
    show_parser = subparsers.add_parser("show-portfolio")
    show_parser.add_argument("--base", default="USD")

    # buy
    buy_parser = subparsers.add_parser("buy")
    buy_parser.add_argument("--currency", required=True)
    buy_parser.add_argument("--amount", type=float, required=True)

    # sell
    sell_parser = subparsers.add_parser("sell")
    sell_parser.add_argument("--currency", required=True)
    sell_parser.add_argument("--amount", type=float, required=True)

    # get-rate
    rate_parser = subparsers.add_parser("get-rate")
    rate_parser.add_argument("--from", dest="from_currency", required=True)
    rate_parser.add_argument("--to", dest="to_currency", required=True)

    # update-rates
    update_parser = subparsers.add_parser("update-rates")
    update_parser.add_argument("--source", choices=["exchangerate"], default=None)

    # show-rates
    showrates_parser = subparsers.add_parser("show-rates")
    showrates_parser.add_argument("--currency", default=None)
    showrates_parser.add_argument("--top", type=int, default=None)
    showrates_parser.add_argument("--base", default="USD")

    args = parser.parse_args()

    if args.command == "register":
        try:
            user_id = register_user(args.username, args.password)
            print(f"Пользователь '{args.username}' зарегистрирован (id={user_id}). Войдите: login --username {args.username} --password ****")
        except Exception as e:
            print(e)

    elif args.command == "login":
        try:
            user_id = login_user(args.username, args.password)
            CURRENT_USER["user_id"] = user_id
            CURRENT_USER["username"] = args.username
            print(f"Вы вошли как '{args.username}'")
        except Exception as e:
            print(e)

    elif args.command == "show-portfolio":
        if not CURRENT_USER["user_id"]:
            print("Сначала выполните login")
            return
        try:
            show_portfolio(CURRENT_USER["user_id"], base=args.base)
        except Exception as e:
            print(e)

    elif args.command == "buy":
        if not CURRENT_USER["user_id"]:
            print("Сначала выполните login")
            return
        try:
            buy_currency(CURRENT_USER["user_id"], args.currency, args.amount)
        except CurrencyNotFoundError as e:
            print(e)
        except Exception as e:
            print(e)

    elif args.command == "sell":
        if not CURRENT_USER["user_id"]:
            print("Сначала выполните login")
            return
        try:
            sell_currency(CURRENT_USER["user_id"], args.currency, args.amount)
        except InsufficientFundsError as e:
            print(e)
        except CurrencyNotFoundError as e:
            print(e)
        except Exception as e:
            print(e)

    elif args.command == "get-rate":
        try:
            rate, updated_at = get_rate(args.from_currency, args.to_currency)
            print(f"Курс {args.from_currency}→{args.to_currency}: {rate} (обновлено: {updated_at})")
        except CurrencyNotFoundError as e:
            print(e)
        except ApiRequestError as e:
            print(e)

    elif args.command == "update-rates":
        try:
            total_updated = update_rates(source=args.source)
            print(f"Update successful. Total rates updated: {total_updated} (last refresh: {datetime.utcnow().isoformat()}Z)")
        except ApiRequestError as e:
            print(e)

    elif args.command == "show-rates":
        try:
            show_rates(currency=args.currency, top=args.top, base=args.base)
        except Exception as e:
            print(e)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()






