import os
import json
from valutatrade_hub.core.models import User
from valutatrade_hub.core.exceptions import InsufficientFundsError, CurrencyNotFoundError, ApiRequestError

USERS_FILE = "data/users.json"
PORTFOLIOS_FILE = "data/portfolios.json"
RATES_FILE = "data/rates.json"

# -----------------------------
# Общие функции для JSON
# -----------------------------
def _load_json(file_path):
    if not os.path.exists(file_path):
        if file_path.endswith("rates.json"):
            return {"pairs": {}, "last_refresh": None}
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# -----------------------------
# Пользователи
# -----------------------------
def load_users():
    return _load_json(USERS_FILE)

def save_users(users):
    _save_json(USERS_FILE, users)

def register_user(username: str, password: str) -> User:
    users = load_users()
    if any(u["username"] == username for u in users):
        raise ValueError("Пользователь с таким именем уже существует")
    user_id = max([u["user_id"] for u in users], default=0) + 1
    user = {"user_id": user_id, "username": username, "password": password}
    users.append(user)
    save_users(users)

    # Портфель
    portfolios = _load_json(PORTFOLIOS_FILE)
    portfolios.append({"user_id": user_id, "wallets": []})
    _save_json(PORTFOLIOS_FILE, portfolios)
    return user

def login_user(username: str, password: str) -> User:
    users = load_users()
    user = next((u for u in users if u["username"] == username), None)
    if not user or user["password"] != password:
        raise ValueError("Неверный логин или пароль")
    return user

# -----------------------------
# Портфель
# -----------------------------
def show_portfolio(user_id: int, base_currency="USD"):
    portfolios = _load_json(PORTFOLIOS_FILE)
    portfolio = next((p for p in portfolios if p["user_id"] == user_id), None)
    if not portfolio:
        print("Портфель пуст")
        return
    for wallet in portfolio["wallets"]:
        print(f"{wallet['currency']}: {wallet['balance']}")

def buy_currency(user_id: int, currency: str, amount: float):
    portfolios = _load_json(PORTFOLIOS_FILE)
    portfolio = next((p for p in portfolios if p["user_id"] == user_id), None)
    if portfolio is None:
        portfolio = {"user_id": user_id, "wallets": []}
        portfolios.append(portfolio)
    wallet = next((w for w in portfolio["wallets"] if w["currency"] == currency), None)
    if not wallet:
        wallet = {"currency": currency, "balance": 0.0}
        portfolio["wallets"].append(wallet)
    wallet["balance"] += amount
    _save_json(PORTFOLIOS_FILE, portfolios)

def sell_currency(user_id: int, currency: str, amount: float):
    portfolios = _load_json(PORTFOLIOS_FILE)
    portfolio = next((p for p in portfolios if p["user_id"] == user_id), None)
    if not portfolio:
        raise InsufficientFundsError("Нет такого пользователя")
    wallet = next((w for w in portfolio["wallets"] if w["currency"] == currency), None)
    if not wallet or wallet["balance"] < amount:
        raise InsufficientFundsError("Недостаточно средств")
    wallet["balance"] -= amount
    _save_json(PORTFOLIOS_FILE, portfolios)

# -----------------------------
# Курсы
# -----------------------------
def get_rate(from_currency: str, to_currency: str):
    data = _load_json(RATES_FILE)
    pair_key = f"{from_currency.upper()}_{to_currency.upper()}"
    pair = data.get("pairs", {}).get(pair_key)
    if not pair:
        raise CurrencyNotFoundError(f"Курс для {pair_key} не найден")
    return pair["rate"], pair["updated_at"]

def update_rates(source=None):
    from valutatrade_hub.parser_service.updater import RatesUpdater
    updater = RatesUpdater(source=source)
    return updater.run_update()















