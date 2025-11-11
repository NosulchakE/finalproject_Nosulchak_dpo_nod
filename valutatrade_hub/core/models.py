# valutatrade_hub/core/models.py

import hashlib
import datetime
from typing import Dict


class User:
    def __init__(self, user_id: int, username: str, password: str, salt: str, registration_date: str | None = None):
        if not username:
            raise ValueError("Имя пользователя не может быть пустым.")
        if len(password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов.")

        self._user_id = user_id
        self._username = username
        self._salt = salt
        self._hashed_password = self._hash_password(password, salt)
        self._registration_date = (
            datetime.datetime.fromisoformat(registration_date)
            if registration_date
            else datetime.datetime.now()
        )

    def _hash_password(self, password: str, salt: str) -> str:
        """Возвращает SHA256-хеш пароля с солью."""
        return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()

    # -----------------------------
    # Методы пользователя
    # -----------------------------
    def get_user_info(self) -> dict:
        """Возвращает информацию о пользователе без пароля."""
        return {
            "user_id": self._user_id,
            "username": self._username,
            "salt": self._salt,
            "registration_date": self._registration_date.isoformat(),
        }

    def change_password(self, new_password: str):
        """Изменяет пароль пользователя."""
        if len(new_password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов.")
        self._hashed_password = self._hash_password(new_password, self._salt)

    def verify_password(self, password: str) -> bool:
        """Проверяет корректность введённого пароля."""
        return self._hashed_password == self._hash_password(password, self._salt)

    # -----------------------------
    # Геттеры и сеттеры
    # -----------------------------
    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, value: str):
        if not value:
            raise ValueError("Имя пользователя не может быть пустым.")
        self._username = value

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def registration_date(self) -> datetime.datetime:
        return self._registration_date


# ==============================================================
# WALLET
# ==============================================================

class Wallet:
    def __init__(self, currency_code: str, balance: float = 0.0):
        if not isinstance(currency_code, str):
            raise TypeError("Код валюты должен быть строкой.")
        if not isinstance(balance, (int, float)) or balance < 0:
            raise ValueError("Баланс должен быть неотрицательным числом.")

        self.currency_code = currency_code
        self._balance = float(balance)

    # -----------------------------
    # Методы кошелька
    # -----------------------------
    def deposit(self, amount: float):
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной.")
        self._balance += amount

    def withdraw(self, amount: float):
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной.")
        if amount > self._balance:
            raise ValueError("Недостаточно средств на балансе.")
        self._balance -= amount

    def get_balance_info(self) -> dict:
        return {"currency_code": self.currency_code, "balance": self._balance}

    # -----------------------------
    # Свойства
    # -----------------------------
    @property
    def balance(self) -> float:
        return self._balance

    @balance.setter
    def balance(self, value: float):
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("Баланс должен быть неотрицательным числом.")
        self._balance = float(value)


# ==============================================================
# PORTFOLIO
# ==============================================================

class Portfolio:
    def __init__(self, user_id: int, wallets: Dict[str, Wallet] | None = None):
        self._user_id = user_id
        self._wallets = wallets if wallets else {}

    def add_currency(self, currency_code: str):
        """Добавляет новый кошелёк, если такого ещё нет."""
        if currency_code in self._wallets:
            raise ValueError(f"Кошелёк для валюты {currency_code} уже существует.")
        self._wallets[currency_code] = Wallet(currency_code)

    def get_wallet(self, currency_code: str) -> Wallet:
        """Возвращает объект кошелька по коду валюты."""
        if currency_code not in self._wallets:
            raise KeyError(f"Кошелёк с валютой {currency_code} не найден.")
        return self._wallets[currency_code]

    def get_total_value(self, base_currency: str = "USD") -> float:
        """Вычисляет общую стоимость всех валют в базовой валюте."""
        exchange_rates = {
            "USD": 1.0,
            "EUR": 1.1,
            "BTC": 68000.0,
        }

        total = 0.0
        for code, wallet in self._wallets.items():
            rate = exchange_rates.get(code)
            if rate is None:
                raise ValueError(f"Нет курса для валюты {code}.")
            total += wallet.balance * (rate / exchange_rates[base_currency])
        return total

    # -----------------------------
    # Свойства
    # -----------------------------
    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def wallets(self) -> Dict[str, Wallet]:
        """Возвращает копию словаря кошельков."""
        return self._wallets.copy()
