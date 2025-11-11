# valutatrade_hub/core/usecases.py
import json
from datetime import datetime, timezone
from pathlib import Path
from hashlib import sha256

from .models import User, Portfolio, Wallet
from .exceptions import InsufficientFundsError, CurrencyNotFoundError
from .decorators import log_action
from ..infra.database import DatabaseManager
from ..infra.settings import SettingsLoader

DATA_DIR = Path("data")
USERS_FILE = DATA_DIR / "users.json"
PORTFOLIOS_FILE = DATA_DIR / "portfolios.json"
RATES_FILE = DATA_DIR / "rates.json"

settings = SettingsLoader()
db = DatabaseManager()

# Вспомогательные функции
def hash_password(password: str, salt: str) -> str:
    return sha256(f"{password}{salt}".encode("utf-8")).hexdigest()

def load_json(file_path: Path) -> dict:
    if not file_path.exists():
        return {}
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file_path: Path, data: dict):
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# --- Пользовательские операции ---
def get_next_user_id() -> int:
    users = load_json(USERS_FILE)
    if not users:
        return 1
    return max(u["user_id"] for u in users) + 1

@log_action(action="REGISTER")
def register(username: str, password: str) -> User:
    if not username.strip():
        raise ValueError("Username не может быть пустым")
    if len(password) < 4:
        raise ValueError("Пароль должен быть не короче 4 символов")

    users = load_json(USERS_FILE)
    if any(u["username"] == username for u in users):
        raise ValueError(f"Имя пользователя '{username}' уже занято")

    user_id = get_next_user_id()
    salt = sha256(f"{user_id}{datetime.now().isoformat()}".encode()).hexdigest()[:8]
    hashed_password = hash_password(password, salt)
    user = User(user_id, username, hashed_password, salt, datetime.now(timezone.utc))

    users.append({
        "user_id": user.user_id,
        "username": user.username,
        "hashed_password": user.hashed_password,
        "salt": user.salt,
        "registration_date": user.registration_date.isoformat()
    })
    save_json(USERS_FILE, users)

    # Создаем пустой портфель
    portfolios = load_json(PORTFOLIOS_FILE)
    portfolios.append({"user_id": user.user_id, "wallets": {}})
    save_json(PORTFOLIOS_FILE, portfolios)

    return user

# --- Авторизация ---
@log_action(action="LOGIN")
def login(username: str, password: str) -> User:
    users = load_json(USERS_FILE)
    data = next((u for u in users if u["username"] == username), None)
    if not data:
        raise ValueError(f"Пользователь '{username}' не найден")
    user = User(
        data["user_id"],
        data["username"],
        data["hashed_password"],
        data["salt"],
        datetime.fromisoformat(data["registration_date"])
    )
    if not user.verify_password(password):
        raise ValueError("Неверный пароль")
    return user

# --- Портфель ---
def load_portfolio(user_id: int) -> Portfolio:
    portfolios = load_json(PORTFOLIOS_FILE)
    data = next((p for p in portfolios if p["user_id"] == user_id), None)
    if not data:
        # создаем новый портфель
        return Portfolio(user_id)
    wallet_objs = {code: Wallet(code, w["balance"]) for code, w in data["wallets"].items()}
    return Portfolio(user_id, wallet_objs)

def save_portfolio(portfolio: Portfolio):
    portfolios = load_json(PORTFOLIOS_FILE)
    for i, p in enumerate(portfolios):
        if p["user_id"] == portfolio.user_id:
            portfolios[i]["wallets"] = {c: {"balance": w.balance} for c, w in portfolio.wallets.items()}
            break
    else:
        portfolios.append({"user_id": portfolio.user_id, "wallets": {c: {"balance": w.balance} for c, w in portfolio.wallets.items()}})
    save_json(PORTFOLIOS_FILE, portfolios)

# --- Валютные операции ---
@log_action(action="BUY")
def buy(user_id: int, currency_code: str, amount: float, base_currency="USD"):
    if amount <= 0:
        raise ValueError("'amount' должен быть положительным числом")
    currency_code = currency_code.upper()

    # Загрузка курсов
    rates_data = load_json(RATES_FILE)
    pair_key = f"{currency_code}_{base_currency}"
    rate_info = rates_data.get("pairs", {}).get(pair_key)
    if not rate_info:
        raise CurrencyNotFoundError(currency_code)
    rate = rate_info["rate"]

    # Загрузка портфеля
    portfolio = load_portfolio(user_id)
    if currency_code not in portfolio.wallets:
        portfolio.add_currency(currency_code)
    wallet = portfolio.get_wallet(currency_code)
    prev_balance = wallet.balance
    wallet.deposit(amount)
    save_portfolio(portfolio)

    return {"currency": currency_code, "amount": amount, "rate": rate, "prev_balance": prev_balance, "new_balance": wallet.balance}

@log_action(action="SELL")
def sell(user_id: int, currency_code: str, amount: float, base_currency="USD"):
    if amount <= 0:
        raise ValueError("'amount' должен быть положительным числом")
    currency_code = currency_code.upper()

    portfolio = load_portfolio(user_id)
    wallet = portfolio.get_wallet(currency_code)
    if wallet is None:
        raise InsufficientFundsError(0, amount, currency_code)
    if wallet.balance < amount:
        raise InsufficientFundsError(wallet.balance, amount, currency_code)

    # Курс
    rates_data = load_json(RATES_FILE)
    pair_key = f"{currency_code}_{base_currency}"
    rate_info = rates_data.get("pairs", {}).get(pair_key)
    if not rate_info:
        raise CurrencyNotFoundError(currency_code)
    rate = rate_info["rate"]

    prev_balance = wallet.balance
    wallet.withdraw(amount)
    save_portfolio(portfolio)

    return {"currency": currency_code, "amount": amount, "rate": rate, "prev_balance": prev_balance, "new_balance": wallet.balance}

def get_rate(from_code: str, to_code: str):
    from_code = from_code.upper()
    to_code = to_code.upper()
    rates_data = load_json(RATES_FILE)
    pair_key = f"{from_code}_{to_code}"
    rate_info = rates_data.get("pairs", {}).get(pair_key)
    if not rate_info:
        raise CurrencyNotFoundError(pair_key)
    return {"rate": rate_info["rate"], "updated_at": rate_info["updated_at"], "source": rate_info["source"]}



