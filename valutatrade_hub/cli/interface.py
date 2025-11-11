# valutatrade_hub/cli/interface.py
import argparse
import json
from datetime import datetime
from valutatrade_hub.parser_service.updater import RatesUpdater
from valutatrade_hub.parser_service.config import ParserConfig

def update_rates_command(args):
    updater = RatesUpdater()
    try:
        updater.run_update()
        print(f"Update successful. Rates written to {ParserConfig().RATES_FILE_PATH}")
    except Exception as e:
        print(f"Update failed: {e}")

def show_rates_command(args):
    config = ParserConfig()
    try:
        with open(config.RATES_FILE_PATH, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Локальный кеш курсов пуст. Выполните 'update-rates'.")
        return

    pairs = data.get("pairs", {})
    last_refresh = data.get("last_refresh", "N/A")

    # фильтры
    if args.currency:
        pairs = {k: v for k, v in pairs.items() if args.currency.upper() in k}

    if args.base:
        # оставить только пары с указанной базой
        pairs = {k: v for k, v in pairs.items() if k.endswith(f"_{args.base.upper()}")}

    if args.top:
        # отсортировать по значению курса и взять top N
        pairs = dict(sorted(pairs.items(), key=lambda item: item[1]["rate"], reverse=True)[:args.top])

    if not pairs:
        print("Нет данных по указанным фильтрам.")
        return

    print(f"Rates from cache (updated at {last_refresh}):")
    for k, v in pairs.items():
        print(f"- {k}: {v['rate']} (source: {v['source']})")

def main():
    parser = argparse.ArgumentParser(description="ValutaTrade CLI")
    subparsers = parser.add_subparsers(dest="command")

    # update-rates
    parser_update = subparsers.add_parser("update-rates", help="Обновить курсы валют")
    parser_update.set_defaults(func=update_rates_command)

    # show-rates
    parser_show = subparsers.add_parser("show-rates", help="Показать локальные курсы")
    parser_show.add_argument("--currency", type=str, help="Фильтр по валюте (например, BTC)")
    parser_show.add_argument("--top", type=int, help="Показать N самых дорогих валют")
    parser_show.add_argument("--base", type=str, help="Базовая валюта для отображения")
    parser_show.set_defaults(func=show_rates_command)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()




