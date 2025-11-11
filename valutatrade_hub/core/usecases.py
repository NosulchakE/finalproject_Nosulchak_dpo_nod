# valutatrade_hub/core/usecases.py
import json
import hashlib
import os
from datetime import datetime, timezone
import requests

from valutatrade_hub.core.exceptions import (
    InsufficientFundsError,
    CurrencyNotFoundError,
    ApiRequestError
)
from valutatrade_hub.infra.settings import SettingsLoader

DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
PORTFOLIOS_FILE = os.path.join(DATA_DIR, "portfolios.json")
RATES_FILE = os.path.join(DATA_DIR, "rates.json")

# -------------------------
# Пользователи
# -------------------------
def _load_json(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def register_user(username: str, password: str):
    if not username:
        raise ValueError("Имя пользователя не может быть пустым")
    if len(password) < 4:
        raise ValueError("Пароль должен быть не короче 4 символов")

    users = _load_json(USERS_FILE)
    if any(u["username"] == username for u in users):
        raise ValueError(f"Имя пользователя '{username}' уже занято")

    salt = os.urandom(8).hex()
    hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()
    user_id = max([u["user_id"] for u in users], default=0) + 1
    user = {
        "user_id": user_id,
        "username": username,
        "hashed_password": hashed_password,
        "salt": salt,
        "registration_date": datetime.now(timezone.utc).isoformat()
    }
    users.append(user)
    _save_json(USERS_FILE, users)

    # Создаём пустой портфель
    portfolios = _load_json(PORTFOLIOS_FILE)
    portfolios.append({"user_id": user_id, "wallets": {}})
    _save_json(PORTFOLIOS_FILE, portfolios)
    return user_id

def login_user(username: str, password: str):
    users = _load_json(USERS_FILE)
    user = next((u for u in users if u["username"] == username), None)
    if not user:
        raise ValueError(f"Пользователь '{username}' не найден")

    hashed_check = hashlib.sha256((password + user["salt"]).encode()).hexdigest()
    if hashed_check != user["hashed_password"]:
        raise ValueError("Неверный пароль")
    return user["user_id"]

# -------------------------
# Портфель
# -------------------------
def show_portfolio(user_id: int, base="USD"):
    portfolios = _load_json(PORTFOLIOS_FILE)
    portfolio = next((p for p in portfolios if p["user_id"] == user_id), None)
    if not portfolio or not portfolio["wallets"]:
        print("Кошельки отсутствуют")
        return

    rates = _load_json(RATES_FILE).get("pairs", {})
    total_base = 0.0
    print(f"Портфель пользователя (база: {base}):")
    for code, wallet in portfolio["wallets"].items():
        balance = wallet["balance"]
        pair_key = f"{code}_{base}"
        rate = rates.get(pair_key, {}).get("rate", 1.0)
        value_base = balance * rate
        total_base += value_base
        print(f"- {code}: {balance:.4f} → {value_base:.2f} {base}")
    print("-" * 30)
    print(f"ИТОГО: {total_base:.2f} {base}")

def buy_currency(user_id: int, currency_code: str, amount: float):
    if amount <= 0:
        raise ValueError("'amount' должен быть положительным числом")
    portfolios = _load_json(PORTFOLIOS_FILE)
    portfolio = next((p for p in portfolios if p["user_id"] == user_id), None)
    if not portfolio:
        raise ValueError("Портфель не найден")

    wallets = portfolio["wallets"]
    if currency_code not in wallets:
        wallets[currency_code] = {"balance": 0.0}

    wallets[currency_code]["balance"] += amount
    _save_json(PORTFOLIOS_FILE, portfolios)
    print(f"Покупка выполнена: {amount:.4f} {currency_code}")

def sell_currency(user_id: int, currency_code: str, amount: float):
    if amount <= 0:
        raise ValueError("'amount' должен быть положительным числом")
    portfolios = _load_json(PORTFOLIOS_FILE)
    portfolio = next((p for p in portfolios if p["user_id"] == user_id), None)
    if not portfolio:
        raise ValueError("Портфель не найден")
    wallets = portfolio["wallets"]
    if currency_code not in wallets:
        raise InsufficientFundsError(f"У вас нет кошелька '{currency_code}'")
    if wallets[currency_code]["balance"] < amount:
        raise InsufficientFundsError(f"Недостаточно средств: доступно {wallets[currency_code]['balance']:.4f} {currency_code}, требуется {amount:.4f} {currency_code}")

    wallets[currency_code]["balance"] -= amount
    _save_json(PORTFOLIOS_FILE, portfolios)
    print(f"Продажа выполнена: {amount:.4f} {currency_code}")

# -------------------------
# Курсы валют
# -------------------------
def get_rate(from_currency: str, to_currency: str):
    rates = _load_json(RATES_FILE).get("pairs", {})
    pair_key = f"{from_currency.upper()}_{to_currency.upper()}"
    if pair_key not in rates:
        raise CurrencyNotFoundError(f"Курс для '{pair_key}' не найден")
    rate = rates[pair_key]["rate"]
    updated_at = rates[pair_key]["updated_at"]
    return rate, updated_at

def update_rates(source=None):
    cfg = SettingsLoader()
    url = f"https://v6.exchangerate-api.com/v6/{cfg.EXCHANGERATE_API_KEY}/latest/USD"
    try:
        resp = requests.get(url, timeout=cfg.REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        if data.get("result") != "success":
            raise ApiRequestError("Ошибка при запросе ExchangeRate-API")
        pairs = {}
        timestamp = datetime.utcnow().isoformat() + "Z"
        for code, rate in data["rates"].items():
            pairs[f"{code}_USD"] = {"rate": rate, "updated_at": timestamp, "source": "ExchangeRate-API"}

        rates_json = {"pairs": pairs, "last_refresh": timestamp}
        _save_json(RATES_FILE, rates_json)
        return len(pairs)
    except requests.exceptions.RequestException as e:
        raise ApiRequestError(str(e))

def show_rates(currency=None, top=None, base="USD"):
    data = _load_json(RATES_FILE)
    pairs = data.get("pairs", {})
    filtered = {}
    for pair, info in pairs.items():
        if currency and not pair.startswith(currency.upper()):
            continue
        filtered[pair] = info

    # сортировка по значению курса (descending) если top задан
    if top:
        filtered = dict(sorted(filtered.items(), key=lambda x: x[1]["rate"], reverse=True)[:top])

    print(f"Rates from cache (updated at {data.get('last_refresh', 'N/A')}):")
    for pair, info in filtered.items():
        print(f"- {pair}: {info['rate']}")





