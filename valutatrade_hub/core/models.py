import hashlib
import secrets
from datetime import datetime
from copy import deepcopy
from .exceptions import InsufficientFundsError

class User:
    """Пользователь системы"""

    def __init__(
        self,
        user_id: int,
        username: str,
        hashed_password: str | None = None,
        salt: str | None = None,
        registration_date: datetime | None = None,
    ):
        if not username:
            raise ValueError("Имя пользователя не может быть пустым")

        self._user_id = user_id
        self._username = username
        self._salt = salt
        self._hashed_password = hashed_password
        self._registration_date = registration_date or datetime.now()

    # пароли
    def change_password(self, new_password: str) -> None:
        if len(new_password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов")

        self._salt = secrets.token_hex(8)
        self._hashed_password = hashlib.sha256(
            (new_password + self._salt).encode()
        ).hexdigest()

    def verify_password(self, password: str) -> bool:
        if not self._salt or not self._hashed_password:
            return False

        hashed = hashlib.sha256(
            (password + self._salt).encode()
        ).hexdigest()

        return hashed == self._hashed_password

    # информация

    def get_user_info(self) -> dict:
        return {
            "user_id": self._user_id,
            "username": self._username,
            "registration_date": self._registration_date.isoformat(),
        }

    # сериализация
    def to_dict(self) -> dict:
        return {
            "user_id": self._user_id,
            "username": self._username,
            "hashed_password": self._hashed_password,
            "salt": self._salt,
            "registration_date": self._registration_date.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            user_id=data["user_id"],
            username=data["username"],
            hashed_password=data.get("hashed_password"),
            salt=data.get("salt"),
            registration_date=datetime.fromisoformat(
                data["registration_date"]
            ) if data.get("registration_date") else None,
        )

    # Геттеры / Сеттеры 

    @property
    def user_id(self):
        return self._user_id

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value: str):
        if not value:
            raise ValueError("Имя пользователя не может быть пустым")
        self._username = value

    @property
    def registration_date(self):
        return self._registration_date


# __________________

class Wallet:
    """Кошелёк для одной валюты"""

    def __init__(self, currency_code: str, balance: float = 0.0):
        if not currency_code:
            raise ValueError("Код валюты не может быть пустым")

        self.currency_code = currency_code.upper()
        self.balance = balance  # используем setter

    def deposit(self, amount: float) -> None:
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("'amount' должен быть положительным числом")

        self._balance += float(amount)

    def withdraw(self, amount: float) -> None:
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("'amount' должен быть положительным числом")

        if amount > self._balance:
            raise InsufficientFundsError(
                available=self._balance,
                required=amount,
                code=self.currency_code
            )

        self._balance -= float(amount)

    def get_balance_info(self) -> str:
        return f"{self.currency_code}: {self._balance:.4f}"

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value: float):
        if not isinstance(value, (int, float)):
            raise ValueError("Баланс должен быть числом")

        if value < 0:
            raise ValueError("Баланс не может быть отрицательным")

        self._balance = float(value)


# _______________


class Portfolio:
    """Портфель пользователя"""

    def __init__(self, user_id: int):
        self._user_id = user_id
        self._wallets: dict[str, Wallet] = {}

    def add_currency(self, currency_code: str) -> None:
        if not currency_code:
            raise ValueError("Код валюты не может быть пустым")

        currency_code = currency_code.upper()

        if currency_code in self._wallets:
            raise ValueError(f"Кошелек '{currency_code}' уже существует")

        self._wallets[currency_code] = Wallet(currency_code)

    def get_wallet(self, currency_code: str) -> Wallet | None:
        return self._wallets.get(currency_code.upper())

    def get_total_value(self, rates: dict, base_currency: str = "USD") -> float:
        """
        rates ожидается в формате:
        {
            "pairs": {
                "BTC_USD": { "rate": 59337.21 },
                ...
            }
        }
        """
        total = 0.0

        pairs = rates.get("pairs", {})

        for code, wallet in self._wallets.items():
            if code == base_currency:
                total += wallet.balance
                continue

            pair_key = f"{code}_{base_currency}"
            rate_info = pairs.get(pair_key)

            if rate_info:
                rate = rate_info["rate"]
                total += wallet.balance * rate

        return total

    @property
    def user_id(self):
        return self._user_id

    @property
    def wallets(self):
        return deepcopy(self._wallets)








