# valutatrade_hub/core/usecases.py
import os
import json
from datetime import datetime

from valutatrade_hub.core.users import User, Portfolio, Wallet, get_user_by_username, save_users, save_portfolios
from valutatrade_hub.parser_service.updater import RatesUpdater
from valutatrade_hub.core.exceptions import InsufficientFundsError, CurrencyNotFoundError, ApiRequestError

USERS_FILE = os.path.join("data", "users.json")
PORTFOLIOS_FILE = os.path.join("data", "portfolios.json")
RATES_FILE = os.path.join("data", "rates.json")


def register_user(username: str, password: str) -> User:
    """Регистрация нового пользователя"""
    users = _load_json(USERS_FILE)
    if any(u["username"] == username for u in users):
        raise ValueError("Пользователь с таким именем уже существует")
    user_id = max([u["user_id"] for u in users], default=0) + 1
    user = User(user_id=user_id, username=username, password=password)
    users.append(user.to_dict())
    save_users(users)
    # Создаем пустой портфель
    portfolios = _load_json(PORTFOLIOS_FILE)
    portfolios.append({"user_id": user_id, "wallets": []})
    save_portfolios(portfolios)
    return user


def login_user(username: str, password: str) -> User:
    """Авторизация пользователя"""
    user = get_user_by_username(username)
    if not user or not user.check_password(password):
        raise ValueError("Неверное имя пользователя или пароль")
    return user


def show_portfolio(user_id: int, base_currency="USD") -> None:
    """Показать портфель пользователя с оценкой в базовой валюте"""
    portfolio_data = _load_portfolio(user_id)
    rates = _load_rates()
    total_value = 0.0
    print(f"Портфель пользователя {user_id} (в {base_currency}):")
    for wallet_data in portfolio_data["wallets"]:
        currency = wallet_data["currency"]
        balance = wallet_data["balance"]
        rate = rates.get(currency, {}).get(base_currency)
        if rate is None:
            print(f"- {currency}: {balance} (нет курса для конвертации в {base_currency})")
            continue
        value = balance * rate
        total_value += value
        print(f"- {currency}: {balance} → {value:.2f} {base_currency}")
    print(f"Общая стоимость: {total_value:.2f} {base_currency}")


def buy_currency(user_id: int, currency: str, amount: float) -> None:
    """Покупка валюты"""
    if amount <= 0:
        raise ValueError("Сумма должна быть положительной")
    portfolio = _load_portfolio(user_id)
    wallet = _get_or_create_wallet(portfolio, currency)
    wallet["balance"] += amount
    _save_portfolio(portfolio)


def sell_currency(user_id: int, currency: str, amount: float) -> None:
    """Продажа валюты"""
    if amount <= 0:
        raise ValueError("Сумма должна быть положительной")
    portfolio = _load_portfolio(user_id)
    wallet = _get_or_create_wallet(portfolio, currency)
    if wallet["balance"] < amount:
        raise InsufficientFundsError(f"Недостаточно средств: {wallet['balance']} {currency}")
    wallet["balance"] -= amount
    _save_portfolio(portfolio)


def get_rate(from_currency: str, to_currency: str):
    """Получить курс валюты из кэша rates.json"""
    rates = _load_rates()
    pair = rates.get(from_currency.upper())
    if not pair or to_currency.upper() not in pair:
        raise CurrencyNotFoundError(f"Курс {from_currency}->{to_currency} не найден")
    rate_info = pair[to_currency.upper()]
    return rate_info["rate"], rate_info.get("timestamp", "N/A")


# ======== Вспомогательные функции ========

def _load_json(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_portfolio(user_id: int):
    portfolios = _load_json(PORTFOLIOS_FILE)
    for p in portfolios:
        if p["user_id"] == user_id:
            return p
    # если портфель отсутствует, создаём
    p = {"user_id": user_id, "wallets": []}
    portfolios.append(p)
    _save_json(PORTFOLIOS_FILE, portfolios)
    return p


def _save_portfolio(portfolio_data):
    portfolios = _load_json(PORTFOLIOS_FILE)
    for i, p in enumerate(portfolios):
        if p["user_id"] == portfolio_data["user_id"]:
            portfolios[i] = portfolio_data
            break
    _save_json(PORTFOLIOS_FILE, portfolios)


def _get_or_create_wallet(portfolio, currency: str):
    currency = currency.upper()
    for wallet in portfolio["wallets"]:
        if wallet["currency"] == currency:
            return wallet
    wallet = {"currency": currency, "balance": 0.0}
    portfolio["wallets"].append(wallet)
    return wallet


def _load_rates():
    """Загрузить курсы валют из кэша"""
    data = _load_json(RATES_FILE)
    return data.get("pairs", {}) if isinstance(data, dict) else {}









