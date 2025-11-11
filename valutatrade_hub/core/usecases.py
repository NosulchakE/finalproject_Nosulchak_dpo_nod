# valutatrade_hub/core/usecases.py
from datetime import datetime, timedelta
from typing import Optional
from decimal import Decimal

from valutatrade_hub.infra.settings import SettingsLoader
from valutatrade_hub.infra.database import DatabaseManager
from valutatrade_hub.decorators import log_action
from valutatrade_hub.core.models import User, Portfolio, Wallet
from valutatrade_hub.core.currencies import get_currency
from valutatrade_hub.core.exceptions import (
    InsufficientFundsError,
    CurrencyNotFoundError,
    ApiRequestError
)


# === Синглтоны ===
settings = SettingsLoader()
db = DatabaseManager()

USERS_JSON = settings.get("USERS_JSON")
PORTFOLIOS_JSON = settings.get("PORTFOLIOS_JSON")
RATES_JSON = settings.get("RATES_JSON")
BASE_CURRENCY = settings.get("BASE_CURRENCY")
RATES_TTL = settings.get("RATES_TTL_SECONDS", 300)


# === Сессия текущего пользователя ===
_current_user: Optional[User] = None


# === Пользователи ===
@log_action("register")
def register(username: str, password: str) -> User:
    users_data = db.read(USERS_JSON)
    if any(u["username"] == username for u in users_data):
        raise ValueError(f"Имя пользователя '{username}' уже занято")
    if len(password) < 4:
        raise ValueError("Пароль должен быть не короче 4 символов")

    user_id = max([u["user_id"] for u in users_data], default=0) + 1
    user = User(user_id=user_id, username=username)
    user.change_password(password)

    users_data.append(user.to_dict())
    db.write(USERS_JSON, users_data)

    # Создать пустой портфель
    portfolios = db.read(PORTFOLIOS_JSON)
    portfolios.append({"user_id": user_id, "wallets": {}})
    db.write(PORTFOLIOS_JSON, portfolios)

    return user


@log_action("login")
def login(username: str, password: str) -> User:
    global _current_user
    users_data = db.read(USERS_JSON)
    found = next((u for u in users_data if u["username"] == username), None)
    if not found:
        raise ValueError(f"Пользователь '{username}' не найден")

    user = User.from_dict(found)
    if not user.verify_password(password):
        raise ValueError("Неверный пароль")

    _current_user = user
    return user


def get_current_user() -> User:
    if not _current_user:
        raise PermissionError("Сначала выполните login")
    return _current_user


# === Портфель ===
def _load_portfolio(user_id: int) -> Portfolio:
    portfolios = db.read(PORTFOLIOS_JSON)
    data = next((p for p in portfolios if p["user_id"] == user_id), None)
    if not data:
        raise ValueError(f"Портфель пользователя {user_id} не найден")
    return Portfolio.from_dict(data)


def _save_portfolio(portfolio: Portfolio):
    portfolios = db.read(PORTFOLIOS_JSON)
    for i, p in enumerate(portfolios):
        if p["user_id"] == portfolio.user_id:
            portfolios[i] = portfolio.to_dict()
            break
    db.write(PORTFOLIOS_JSON, portfolios)


# === Курсы ===
def _get_rate(from_code: str, to_code: str) -> float:
    rates = db.read(RATES_JSON)
    key = f"{from_code}_{to_code}"
    now = datetime.utcnow()
    info = rates.get(key)
    if not info:
        raise ApiRequestError(f"Курс {key} недоступен")

    updated_at = datetime.fromisoformat(info["updated_at"])
    if (now - updated_at) > timedelta(seconds=RATES_TTL):
        raise ApiRequestError(f"Курс {key} устарел")
    return info["rate"]


# === Покупка ===
@log_action("buy")
def buy(currency_code: str, amount: float):
    if amount <= 0:
        raise ValueError("'amount' должен быть положительным числом")

    user = get_current_user()
    portfolio = _load_portfolio(user.user_id)

    # Проверка валюты
    try:
        get_currency(currency_code)
    except CurrencyNotFoundError as e:
        raise e

    if currency_code not in portfolio.wallets:
        portfolio.add_currency(currency_code)

    wallet = portfolio.get_wallet(currency_code)
    # Опциональная оценка стоимости
    try:
        rate = _get_rate(currency_code, BASE_CURRENCY)
    except ApiRequestError:
        rate = None

    wallet.deposit(amount)
    _save_portfolio(portfolio)

    return {
        "currency": currency_code,
        "amount": amount,
        "wallet_balance": wallet.balance,
        "rate": rate,
        "base": BASE_CURRENCY
    }


# === Продажа ===
@log_action("sell")
def sell(currency_code: str, amount: float):
    if amount <= 0:
        raise ValueError("'amount' должен быть положительным числом")

    user = get_current_user()
    portfolio = _load_portfolio(user.user_id)

    if currency_code not in portfolio.wallets:
        raise InsufficientFundsError(0, amount, currency_code)

    wallet = portfolio.get_wallet(currency_code)
    if wallet.balance < amount:
        raise InsufficientFundsError(wallet.balance, amount, currency_code)

    try:
        rate = _get_rate(currency_code, BASE_CURRENCY)
    except ApiRequestError:
        rate = None

    wallet.withdraw(amount)
    _save_portfolio(portfolio)

    return {
        "currency": currency_code,
        "amount": amount,
        "wallet_balance": wallet.balance,
        "rate": rate,
        "base": BASE_CURRENCY
    }


# === Получение курса ===
@log_action("get_rate")
def get_rate(from_code: str, to_code: str):
    try:
        get_currency(from_code)
        get_currency(to_code)
    except CurrencyNotFoundError as e:
        raise e

    rate = _get_rate(from_code, to_code)
    rates = db.read(RATES_JSON)
    updated_at = rates[f"{from_code}_{to_code}"]["updated_at"]

    return {
        "from": from_code,
        "to": to_code,
        "rate": rate,
        "updated_at": updated_at
    }


