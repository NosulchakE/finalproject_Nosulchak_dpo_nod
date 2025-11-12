# valutatrade_hub/core/usecases.py
import os
import json
from datetime import datetime
from valutatrade_hub.core.models import User, Portfolio, Wallet
from valutatrade_hub.core.exceptions import (
    InsufficientFundsError,
    CurrencyNotFoundError,
    ApiRequestError,
)

USERS_FILE = "data/users.json"
PORTFOLIOS_FILE = "data/portfolios.json"
RATES_FILE = "data/rates.json"

# --- вспомогательные функции для работы с JSON ---
def _load_json(file_path):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# --- Пользователи ---
def register_user(username: str, password: str) -> User:
    users_data = _load_json(USERS_FILE)
    if username in users_data:
        raise ValueError("Пользователь уже существует")
    user = User(username=username, password=password)
    users_data[username] = user.to_dict()
    _save_json(USERS_FILE, users_data)
    return user

def login_user(username: str, password: str) -> User:
    users_data = _load_json(USERS_FILE)
    if username not in users_data:
        raise ValueError("Пользователь не найден")
    user_dict = users_data[username]
    user = User.from_dict(user_dict)
    if not user.check_password(password):
        raise ValueError("Неверный пароль")
    return user

# --- Портфель ---
def show_portfolio(user_id: str, base_currency="USD"):
    portfolios = _load_json(PORTFOLIOS_FILE)
    portfolio = portfolios.get(user_id)
    if not portfolio:
        print("Портфель пуст")
        return
    # Печать портфеля
    for wallet in portfolio["wallets"]:
        print(f"{wallet['currency']}: {wallet['balance']}")

# --- Покупка/Продажа ---
def buy_currency(user_id: str, currency: str, amount: float):
    portfolios = _load_json(PORTFOLIOS_FILE)
    if user_id not in portfolios:
        portfolios[user_id] = {"wallets": []}
    wallets = portfolios[user_id]["wallets"]
    wallet = next((w for w in wallets if w["currency"] == currency), None)
    if not wallet:
        wallet = {"currency": currency, "balance": 0.0}
        wallets.append(wallet)
    wallet["balance"] += amount
    _save_json(PORTFOLIOS_FILE, portfolios)

def sell_currency(user_id: str, currency: str, amount: float):
    portfolios = _load_json(PORTFOLIOS_FILE)
    if user_id not in portfolios:
        raise InsufficientFundsError("Нет такого пользователя")
    wallets = portfolios[user_id]["wallets"]
    wallet = next((w for w in wallets if w["currency"] == currency), None)
    if not wallet or wallet["balance"] < amount:
        raise InsufficientFundsError("Недостаточно средств")
    wallet["balance"] -= amount
    _save_json(PORTFOLIOS_FILE, portfolios)

# --- Курс валют ---
def get_rate(from_currency: str, to_currency: str):
    rates_data = _load_json(RATES_FILE)
    pair_key = f"{from_currency.upper()}_{to_currency.upper()}"
    pair = rates_data.get("pairs", {}).get(pair_key)
    if not pair:
        raise CurrencyNotFoundError(f"Курс для {pair_key} не найден")
    return pair["rate"], pair["updated_at"]

# --- Обновление курсов ---
def update_rates(source=None):
    """Обновление курсов валют через parser_service"""
    # Локальный импорт, чтобы избежать циклического импорта
    from valutatrade_hub.parser_service.updater import RatesUpdater
    updater = RatesUpdater(source=source)
    total_updated = updater.run_update()
    return total_updated











