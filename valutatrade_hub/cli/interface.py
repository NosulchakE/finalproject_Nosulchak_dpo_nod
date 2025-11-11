# valutatrade_hub/cli/interface.py
import argparse
from valutatrade_hub.core.usecases import update_rates, get_rate
from valutatrade_hub.core.exceptions import ApiRequestError, CurrencyNotFoundError

def main():
    parser = argparse.ArgumentParser(description="ValutaTrade CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Команда update-rates
    parser_update = subparsers.add_parser("update-rates", help="Обновить курсы валют")
    
    # Команда get-rate
    parser_get = subparsers.add_parser("get-rate", help="Показать курс валюты")
    parser_get.add_argument("--from", dest="from_currency", required=True, help="Исходная валюта")
    parser_get.add_argument("--to", dest="to_currency", required=True, help="Целевая валюта")

    args = parser.parse_args()

    if args.command == "update-rates":
        try:
            count = update_rates()
            print(f"Update successful. Total rates updated: {count}")
        except ApiRequestError as e:
            print(f"ERROR: {e}")

    elif args.command == "get-rate":
        try:
            rate, updated_at = get_rate(args.from_currency, args.to_currency)
            print(f"Rate {args.from_currency.upper()}→{args.to_currency.upper()}: {rate} (updated: {updated_at})")
        except CurrencyNotFoundError as e:
            print(f"ERROR: {e}")
        except ApiRequestError as e:
            print(f"ERROR: {e}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()








