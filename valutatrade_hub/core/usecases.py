# valutatrade_hub/core/usecases.py
from valutatrade_hub.decorators import log_action
import logging
from valutatrade_hub.core.models import User
from valutatrade_hub.core.exceptions import InsufficientFundsError, CurrencyNotFoundError, ApiRequestError
from valutatrade_hub.parser_service.updater import RatesUpdater
from valutatrade_hub.infra.database import JSONDatabase

# настройка логирования централизованно
logger = logging.getLogger(__name__)

# Используем базу 
_db = JSONDatabase()

@log_action("REGISTER")
def register_user(username: str, password: str) -> dict:
    users = _db.load_users()
    if any(u["username"] == username for u in users):
        raise ValueError("Пользователь с таким именем уже существует")

    user_ids = [int(u["user_id"]) for u in users] if users else [0]
    user_id = max(user_ids) + 1

    user_obj = User.create(username, password)
    user_obj._user_id = user_id  # устанавливаем реальный ID
    user = {
        "user_id": user_id,
        "username": username,
        "salt": user_obj._salt,
        "hashed_password": user_obj._hashed_password
    }

    users.append(user)
    _db.save_users(users)

    # Создаем портфель с начальным балансом
    portfolios = _db.load_portfolios()
    portfolios.append({
        "user_id": user_id,
        "wallets": [{"currency": "USD", "balance": 10000.0}]
    })
    _db.save_portfolios(portfolios)

    logger.info(f"Пользователь '{username}' зарегистрирован с user_id={user_id}")
    return user

@log_action("LOGIN") 
def login_user(username: str, password: str) -> dict:
    users = _db.load_users()
    user = next((u for u in users if u["username"] == username), None)
    if not user:
        raise ValueError("Неверный логин или пароль")

    user_obj = User.from_dict(user)
    if not user_obj.verify_password(password):
        raise ValueError("Неверный логин или пароль")

    logger.info(f"Пользователь '{username}' успешно вошел")
    return user


# Портфель
def show_portfolio(user_id: int, base_currency="USD"):
    portfolios = _db.load_portfolios()
    portfolio = next((p for p in portfolios if p["user_id"] == user_id), None)
    if not portfolio:
        logger.warning("Портфель пуст")
        return

    total_value = 0.0
    logger.info(f"Портфель пользователя (в {base_currency}):")
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
                value = balance

        total_value += value
        logger.info(f"{currency}: {balance:.2f} (~{value:.2f} {base_currency})")

    logger.info(f"Общая стоимость: {total_value:.2f} {base_currency}")



@log_action("BUY")
def buy_currency(user_id: int, currency: str, amount: float):
    if amount <= 0:
        raise ValueError("Сумма должна быть положительной")

    portfolios = _db.load_portfolios()
    portfolio = next((p for p in portfolios if p["user_id"] == user_id), None)
    if portfolio is None:
        portfolio = {"user_id": user_id, "wallets": []}
        portfolios.append(portfolio)

    # ОТДЕЛЬНО ОБРАБАТЫВАЕМ ПОКУПКУ USD
    if currency.upper() == "USD":
        usd_wallet = next((w for w in portfolio["wallets"] if w["currency"] == "USD"), None)
        if not usd_wallet:
            usd_wallet = {"currency": "USD", "balance": 0.0}
            portfolio["wallets"].append(usd_wallet)
        
        usd_wallet["balance"] += amount
        _db.save_portfolios(portfolios)
        logger.info(f"Пополнено {amount:.2f} USD")
        return

    target_wallet = next((w for w in portfolio["wallets"] if w["currency"] == currency), None)
    if not target_wallet:
        target_wallet = {"currency": currency, "balance": 0.0}
        portfolio["wallets"].append(target_wallet)

    usd_wallet = next((w for w in portfolio["wallets"] if w["currency"] == "USD"), None)
    if not usd_wallet:
        raise InsufficientFundsError("Нет USD для покупки")

    try:
        rate, _ = get_rate("USD", currency)
        cost_usd = amount / rate
    except (CurrencyNotFoundError, ApiRequestError) as e:
        raise CurrencyNotFoundError(f"Не удалось получить курс для {currency}: {e}")

    if usd_wallet["balance"] < cost_usd:
        raise InsufficientFundsError(f"Недостаточно USD. Нужно: {cost_usd:.2f}, доступно: {usd_wallet['balance']:.2f}")

    usd_wallet["balance"] -= cost_usd
    target_wallet["balance"] += amount

    _db.save_portfolios(portfolios)
    logger.info(f"Куплено {amount:.2f} {currency} за {cost_usd:.2f} USD (курс: 1 USD = {rate:.4f} {currency})")



@log_action("SELL")
def sell_currency(user_id: int, currency: str, amount: float):
    if amount <= 0:
        raise ValueError("Сумма должна быть положительной")

    portfolios = _db.load_portfolios()
    portfolio = next((p for p in portfolios if p["user_id"] == user_id), None)
    if not portfolio:
        raise InsufficientFundsError("Портфель не найден")

    source_wallet = next((w for w in portfolio["wallets"] if w["currency"] == currency), None)
    if not source_wallet or source_wallet["balance"] < amount:
        raise InsufficientFundsError(f"Недостаточно {currency} для продажи")

    usd_wallet = next((w for w in portfolio["wallets"] if w["currency"] == "USD"), None)
    if not usd_wallet:
        usd_wallet = {"currency": "USD", "balance": 0.0}
        portfolio["wallets"].append(usd_wallet)

    try:
        rate, _ = get_rate(currency, "USD")
        revenue_usd = amount * rate
    except (CurrencyNotFoundError, ApiRequestError) as e:
        raise CurrencyNotFoundError(f"Не удалось получить курс для {currency}: {e}")

    source_wallet["balance"] -= amount
    usd_wallet["balance"] += revenue_usd

    _db.save_portfolios(portfolios)
    logger.info(f"Продано {amount:.2f} {currency} за {revenue_usd:.2f} USD (курс: 1 {currency} = {rate:.4f} USD)")


# Курсы
def get_rate(from_currency: str, to_currency: str):
    if from_currency.upper() == to_currency.upper():
        return 1.0, datetime.now().isoformat()  # курс сам к себе= 1
    
    data = _db.load_rates()
    pair_key = f"{from_currency.upper()}_{to_currency.upper()}"
    pair = data.get("pairs", {}).get(pair_key)
    if not pair:
        raise CurrencyNotFoundError(f"Курс для {pair_key} не найден")
    return pair["rate"], pair["updated_at"]


def update_rates(source=None):
    updater = RatesUpdater(source=source)
    return updater.run_update()



























