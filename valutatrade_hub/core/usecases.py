# valutatrade_hub/core/usecases.py
import os
import json
from datetime import datetime

from valutatrade_hub.core.models import User, Portfolio, Wallet, get_user_by_username, save_users, save_portfolios
from valutatrade_hub.core.exceptions import CurrencyNotFoundError, InsufficientFundsError, ApiRequestError
from valutatrade_hub.parser_service.updater import RatesUpdater

USERS_FILE = "data/users.json"
PORTFOLIOS_FILE = "data/portfolios.json"
RATES_FILE = "data/rates.json"


def register_user(username: str, password: str) -> User:
    users = _load_json(USERS_FILE)
    if any(u["username"] == username for u in users):
        raise ValueError(f"Пользователь {username} уже существует")
    
    user_id = max([u["user_id"] for u in users], default=0) + 1
    user = User(user_id=user_id, username=username, password=password)
    users.append(user.to_dict())
    _save_json(USERS_FILE, users)

    portfolios = _load_json(PORTFOLIOS_FILE)
    if not isinstance(portfolios, list):
        portfolios = []
    portfolios.append({"user_id": user_id, "wallets": []})
    _save_json(PORTFOLIOS_FILE, portfolios)

    return user


def login_user(username: str, password: str) -> User:
    user = get_user_by_username(username)
    if not user or not user.verify_password(password):
        raise ValueError("Неверный логин или пароль")
    return user


def show_portfolio(user_id: int, base_currency: str = "USD"):
    portfolios = _load_json(PORTFOLIOS_FILE)
    portfolio_data = next((p for p in portfolios if p["user_id"] == user_id), None)
    if not portfolio_data:
        print("Портфель пуст")
        return

    portfolio = Portfolio.from_dict(portfolio_data)
    total = portfolio.get_total_value(base=base_currency)
    print(f"Портфель пользователя (в {base_currency}):")
    for wallet in portfolio.wallets:
        print(f"- {wallet.currency}: {wallet.balance}")
    print(f"Общая стоимость: {total} {base_currency}")


def buy_currency(user_id: int, currency: str, amount: float):
    if amount <= 0:
        raise ValueError("Сумма должна быть положительной")

    rates_data = _load_json(RATES_FILE)
    pairs = rates_data.get("pairs", {})
    rate_info = pairs.get(f"{currency.upper()}USD")
    if not rate_info:
        raise CurrencyNotFoundError(f"Курс для {currency} не найден")
    
    portfolio_data = _load_json(PORTFOLIOS_FILE)
    portfolio_entry = next((p for p in portfolio_data if p["user_id"] == user_id), None)
    if not portfolio_entry:
        portfolio_entry = {"user_id": user_id, "wallets": []}
        portfolio_data.append(portfolio_entry)

    portfolio = Portfolio.from_dict(portfolio_entry)
    wallet = portfolio.get_wallet(currency)
    wallet.deposit(amount)
    _save_json(PORTFOLIOS_FILE, [p.to_dict() for p in portfolio_data])


def sell_currency(user_id: int, currency: str, amount: float):
    if amount <= 0:
        raise ValueError("Сумма должна быть положительной")

    rates_data = _load_json(RATES_FILE)
    pairs = rates_data.get("pairs", {})
    rate_info = pairs.get(f"{currency.upper()}USD")
    if not rate_info:
        raise CurrencyNotFoundError(f"Курс для {currency} не найден")

    portfolio_data = _load_json(PORTFOLIOS_FILE)
    portfolio_entry = next((p for p in portfolio_data if p["user_id"] == user_id), None)
    if not portfolio_entry:
        raise ValueError("Портфель пуст")

    portfolio = Portfolio.from_dict(portfolio_entry)
    wallet = portfolio.get_wallet(currency)
    wallet.withdraw(amount)
    _save_json(PORTFOLIOS_FILE, [p.to_dict() for p in portfolio_data])


def get_rate(from_currency: str, to_currency: str):
    rates_data = _load_json(RATES_FILE)
    pairs = rates_data.get("pairs", {})
    pair_key = f"{from_currency.upper()}{to_currency.upper()}"
    rate_info = pairs.get(pair_key)
    if not rate_info:
        raise CurrencyNotFoundError(f"Курс {pair_key} не найден")
    return rate_info["rate"], rates_data.get("last_refresh")


# ---- Вспомогательные функции ----

def _load_json(file_path):
    if not os.path.exists(file_path):
        return [] if "portfolios" in file_path or "users" in file_path else {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(file_path, data):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)









