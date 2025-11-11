# valutatrade_hub/cli/interface.py

import argparse
from valutatrade_hub.core import usecases


def main():
    parser = argparse.ArgumentParser(description="ValutaTrade CLI — управление валютными портфелями")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # ------------------------------
    # Команда: register
    # ------------------------------
    register_parser = subparsers.add_parser("register", help="Регистрация нового пользователя")
    register_parser.add_argument("--username", required=True, help="Имя пользователя")
    register_parser.add_argument("--password", required=True, help="Пароль")

    # ------------------------------
    # Команда: login
    # ------------------------------
    login_parser = subparsers.add_parser("login", help="Вход в систему")
    login_parser.add_argument("--username", required=True, help="Имя пользователя")
    login_parser.add_argument("--password", required=True, help="Пароль")

    # ------------------------------
    # Команда: show-portfolio
    # ------------------------------
    portfolio_parser = subparsers.add_parser("show-portfolio", help="Показать портфель пользователя")
    portfolio_parser.add_argument("--base", default="USD", help="Базовая валюта (по умолчанию USD)")

    # ------------------------------
    # Команда: buy
    # ------------------------------
    buy_parser = subparsers.add_parser("buy", help="Покупка валюты")
    buy_parser.add_argument("--currency", required=True, help="Код валюты (например, BTC)")
    buy_parser.add_argument("--amount", required=True, type=float, help="Количество валюты")

    # ------------------------------
    # Команда: sell
    # ------------------------------
    sell_parser = subparsers.add_parser("sell", help="Продажа валюты")
    sell_parser.add_argument("--currency", required=True, help="Код валюты (например, BTC)")
    sell_parser.add_argument("--amount", required=True, type=float, help="Количество валюты")

    # ------------------------------
    # Команда: get-rate
    # ------------------------------
    rate_parser = subparsers.add_parser("get-rate", help="Получить текущий курс валюты")
    rate_parser.add_argument("--from", dest="from_currency", required=True, help="Исходная валюта (например, USD)")
    rate_parser.add_argument("--to", dest="to_currency", required=True, help="Целевая валюта (например, BTC)")

    args = parser.parse_args()

    # ==============================
    # Обработка команд
    # ==============================
    match args.command:
        case "register":
            usecases.register_user(args.username, args.password)
        case "login":
            usecases.login_user(args.username, args.password)
        case "show-portfolio":
            usecases.show_portfolio(args.base)
        case "buy":
            usecases.buy_currency(args.currency, args.amount)
        case "sell":
            usecases.sell_currency(args.currency, args.amount)
        case "get-rate":
            usecases.get_rate(args.from_currency, args.to_currency)
        case _:
            print("Неизвестная команда.")


if __name__ == "__main__":
    main()
