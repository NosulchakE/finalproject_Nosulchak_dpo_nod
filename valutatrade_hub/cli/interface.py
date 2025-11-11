# valutatrade_hub/cli/interface.py
import argparse
from decimal import Decimal

from valutatrade_hub.core import usecases
from valutatrade_hub.core.exceptions import (
    InsufficientFundsError,
    CurrencyNotFoundError,
    ApiRequestError
)


def main():
    parser = argparse.ArgumentParser(
        description="ValutaTrade CLI — управление кошельками и валютой"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ---------------- Register ----------------
    parser_register = subparsers.add_parser("register")
    parser_register.add_argument("--username", required=True)
    parser_register.add_argument("--password", required=True)

    # ---------------- Login ----------------
    parser_login = subparsers.add_parser("login")
    parser_login.add_argument("--username", required=True)
    parser_login.add_argument("--password", required=True)

    # ---------------- Show Portfolio ----------------
    parser_show = subparsers.add_parser("show-portfolio")
    parser_show.add_argument("--base", default="USD")

    # ---------------- Buy ----------------
    parser_buy = subparsers.add_parser("buy")
    parser_buy.add_argument("--currency", required=True)
    parser_buy.add_argument("--amount", type=float, required=True)

    # ---------------- Sell ----------------
    parser_sell = subparsers.add_parser("sell")
    parser_sell.add_argument("--currency", required=True)
    parser_sell.add_argument("--amount", type=float, required=True)

    # ---------------- Get Rate ----------------
    parser_rate = subparsers.add_parser("get-rate")
    parser_rate.add_argument("--from", dest="from_code", required=True)
    parser_rate.add_argument("--to", dest="to_code", required=True)

    # ---------------- Parse args ----------------
    args = parser.parse_args()

    try:
        if args.command == "register":
            user = usecases.register(args.username, args.password)
            print(f"Пользователь '{user.username}' зарегистрирован (id={user.user_id}). Войдите: login --username {user.username} --password ****")

        elif args.command == "login":
            user = usecases.login(args.username, args.password)
            print(f"Вы вошли как '{user.username}'")

        elif args.command == "show-portfolio":
            user = usecases.get_current_user()
            portfolio = usecases._load_portfolio(user.user_id)
            base = args.base.upper()
            total = 0.0

            print(f"Портфель пользователя '{user.username}' (база: {base}):")
            if not portfolio.wallets:
                print("  Кошельков пока нет")
            else:
                for code, wallet in portfolio.wallets.items():
                    try:
                        rate = usecases._get_rate(code, base)
                        value = wallet.balance * rate
                    except ApiRequestError:
                        rate = None
                        value = None

                    balance_str = f"{wallet.balance:.4f}"
                    if value is not None:
                        print(f"- {code}: {balance_str} → {value:.2f} {base}")
                        total += value
                    else:
                        print(f"- {code}: {balance_str} → (курс недоступен)")

                print("-" * 40)
                print(f"ИТОГО: {total:.2f} {base}")

        elif args.command == "buy":
            res = usecases.buy(args.currency.upper(), args.amount)
            print(f"Покупка выполнена: {res['amount']:.4f} {res['currency']} по курсу {res['rate']:.2f} {res['base']}")
            print(f"Изменения в портфеле: {res['currency']}: стало {res['wallet_balance']:.4f}")

        elif args.command == "sell":
            res = usecases.sell(args.currency.upper(), args.amount)
            print(f"Продажа выполнена: {res['amount']:.4f} {res['currency']} по курсу {res['rate']:.2f} {res['base']}")
            print(f"Изменения в портфеле: {res['currency']}: стало {res['wallet_balance']:.4f}")

        elif args.command == "get-rate":
            rate_info = usecases.get_rate(args.from_code.upper(), args.to_code.upper())
            print(f"Курс {rate_info['from']}→{rate_info['to']}: {rate_info['rate']} (обновлено: {rate_info['updated_at']})")

    except InsufficientFundsError as e:
        print(f"Недостаточно средств: доступно {e.available} {e.code}, требуется {e.required} {e.code}")
    except CurrencyNotFoundError as e:
        print(f"Неизвестная валюта '{e.code}'. Список поддерживаемых кодов: ...")
    except ApiRequestError as e:
        print(f"Ошибка получения курса: {e}")
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()


