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
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# -----------------------------
# Пользователи
# -----------------------------
def load_users():
    return _load_json(USERS_FILE)

def save_users(users):
    _save_json(USERS_FILE, users)

def register_user(username: str, password: str) -> dict:
    users = load_users()
    if any(u["username"] == username for u in users):
        raise ValueError("Пользователь с таким именем уже существует")
    
    # Правильная генерация ID
    user_ids = [int(u["user_id"]) for u in users] if users else [0]
    user_id = max(user_ids) + 1
    
    # Хэширование пароля
    password_hash = User.hash_password(password)
    user = {"user_id": user_id, "username": username, "password_hash": password_hash}
    users.append(user)
    save_users(users)

    # Создаем портфель с начальным балансом
    portfolios = _load_json(PORTFOLIOS_FILE)
    portfolios.append({
        "user_id": user_id, 
        "wallets": [
            {"currency": "USD", "balance": 10000.0}  # начальный баланс
        ]
    })
    _save_json(PORTFOLIOS_FILE, portfolios)
    
    return user

def login_user(username: str, password: str) -> dict:
    users = load_users()
    user = next((u for u in users if u["username"] == username), None)
    password_hash = User.hash_password(password)
    if not user or user["password_hash"] != password_hash:
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
    
    print(f"\nПортфель пользователя (в {base_currency}):")
    print("-" * 40)
    
    total_value = 0.0
    for wallet in portfolio["wallets"]:
        currency = wallet["currency"]
        balance = wallet["balance"]
        
        if currency == base_currency:
            value = balance
        else:
            try:
                rate, _ = get_rate(currency, base_currency)
                value = balance * rate
            except (CurrencyNotFoundError, ApiRequestError):
                value = balance  # если курс не найден, показываем в оригинальной валюте
        
        total_value += value
        print(f"{currency}: {balance:.2f} (~{value:.2f} {base_currency})")
    
    print("-" * 40)
    print(f"Общая стоимость: {total_value:.2f} {base_currency}")

def buy_currency(user_id: int, currency: str, amount: float):
    if amount <= 0:
        raise ValueError("Сумма должна быть положительной")
        
    portfolios = _load_json(PORTFOLIOS_FILE)
    portfolio = next((p for p in portfolios if p["user_id"] == user_id), None)
    if portfolio is None:
        portfolio = {"user_id": user_id, "wallets": []}
        portfolios.append(portfolio)
    
    # Находим или создаем кошелек для покупаемой валюты
    target_wallet = next((w for w in portfolio["wallets"] if w["currency"] == currency), None)
    if not target_wallet:
        target_wallet = {"currency": currency, "balance": 0.0}
        portfolio["wallets"].append(target_wallet)
    
    # Находим USD кошелек для списания
    usd_wallet = next((w for w in portfolio["wallets"] if w["currency"] == "USD"), None)
    if not usd_wallet:
        raise InsufficientFundsError("Нет USD для покупки")
    
    # Получаем курс и рассчитываем стоимость
    try:
        rate, _ = get_rate("USD", currency)  # Сколько валюты получим за 1 USD
        cost_usd = amount / rate
    except (CurrencyNotFoundError, ApiRequestError) as e:
        raise CurrencyNotFoundError(f"Не удалось получить курс для {currency}: {e}")
    
    if usd_wallet["balance"] < cost_usd:
        raise InsufficientFundsError(f"Недостаточно USD. Нужно: {cost_usd:.2f}, доступно: {usd_wallet['balance']:.2f}")
    
    # Выполняем операцию
    usd_wallet["balance"] -= cost_usd
    target_wallet["balance"] += amount
    
    _save_json(PORTFOLIOS_FILE, portfolios)
    print(f"Куплено {amount:.2f} {currency} за {cost_usd:.2f} USD (курс: 1 USD = {rate:.4f} {currency})")

def sell_currency(user_id: int, currency: str, amount: float):
    if amount <= 0:
        raise ValueError("Сумма должна быть положительной")
        
    portfolios = _load_json(PORTFOLIOS_FILE)
    portfolio = next((p for p in portfolios if p["user_id"] == user_id), None)
    if not portfolio:
        raise InsufficientFundsError("Портфель не найден")
    
    # Находим кошелек продаваемой валюты
    source_wallet = next((w for w in portfolio["wallets"] if w["currency"] == currency), None)
    if not source_wallet or source_wallet["balance"] < amount:
        raise InsufficientFundsError(f"Недостаточно {currency} для продажи")
    
    # Находим или создаем USD кошелек
    usd_wallet = next((w for w in portfolio["wallets"] if w["currency"] == "USD"), None)
    if not usd_wallet:
        usd_wallet = {"currency": "USD", "balance": 0.0}
        portfolio["wallets"].append(usd_wallet)
    
    # Получаем курс и рассчитываем выручку
    try:
        rate, _ = get_rate(currency, "USD")  # Сколько USD получим за 1 единицу валюты
        revenue_usd = amount * rate
    except (CurrencyNotFoundError, ApiRequestError) as e:
        raise CurrencyNotFoundError(f"Не удалось получить курс для {currency}: {e}")
    
    # Выполняем операцию
    source_wallet["balance"] -= amount
    usd_wallet["balance"] += revenue_usd
    
    _save_json(PORTFOLIOS_FILE, portfolios)
    print(f"Продано {amount:.2f} {currency} за {revenue_usd:.2f} USD (курс: 1 {currency} = {rate:.4f} USD)")

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

# Функция для текущего пользователя (для декораторов)
def get_current_user():
    """Получить текущего пользователя (для совместимости с декораторами)"""
    from valutatrade_hub.cli.interface import CURRENT_USER
    return CURRENT_USER















