# valutatrade_hub/core/usecases.py

def register_user(username: str, password: str):
    print(f"[DEBUG] Регистрация пользователя: {username} / {password}")


def login_user(username: str, password: str):
    print(f"[DEBUG] Логин пользователя: {username}")


def show_portfolio(base_currency: str = "USD"):
    print(f"[DEBUG] Просмотр портфеля (база: {base_currency})")


def buy_currency(currency_code: str, amount: float):
    print(f"[DEBUG] Покупка: {amount} {currency_code}")


def sell_currency(currency_code: str, amount: float):
    print(f"[DEBUG] Продажа: {amount} {currency_code}")


def get_rate(from_currency: str, to_currency: str):
    print(f"[DEBUG] Получение курса {from_currency}->{to_currency}")
