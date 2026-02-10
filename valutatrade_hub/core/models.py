import hashlib, secrets, datetime

class User:
    """Пользователь системы"""

    def __init__(
        self,
        user_id: int,
        username: str,
        password_hash: str | None = None,
        salt: str | None = None,
        registration_date: str | None = None,
    ):
        if not username:
            raise ValueError("Имя пользователя не может быть пустым")

        self._user_id = user_id
        self._username = username
        self._salt = salt
        self._password_hash = password_hash
        self._registration_date = (
            registration_date
            if registration_date
            else datetime.datetime.now().isoformat()
        )

    # Пароли

    def change_password(self, new_password: str) -> None:
        if len(new_password) < 4:
            raise ValueError("Пароль слишком короткий")

        self._salt = secrets.token_hex(8)
        self._password_hash = hashlib.sha256(
            (new_password + self._salt).encode()
        ).hexdigest()

    def verify_password(self, password: str) -> bool:
        if not self._salt or not self._password_hash:
            return False

        return self._password_hash == hashlib.sha256(
            (password + self._salt).encode()
        ).hexdigest()

    #  Сериализация

    def to_dict(self) -> dict:
        return {
            "user_id": self._user_id,
            "username": self._username,
            "password_hash": self._password_hash,
            "salt": self._salt,
            "registration_date": self._registration_date,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            user_id=data["user_id"],
            username=data["username"],
            password_hash=data.get("password_hash"),
            salt=data.get("salt"),
            registration_date=data.get("registration_date"),
        )

    #  Геттеры как в ТЗ

    @property
    def user_id(self):
        return self._user_id

    @property
    def username(self):
        return self._username


class Wallet:
    def __init__(self, currency_code, balance=0.0):
        if not currency_code:
            raise ValueError("Код валюты не может быть пустым")
        self.currency_code = currency_code.upper()
        self._balance = balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Сумма должна быть > 0")
        self._balance += amount

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Сумма должна быть >  0")
        if amount > self._balance:
            raise ValueError(f"Недостаточно средств: {self._balance}")
        self._balance -= amount

    @property
    def balance(self):
        return self._balance



class Portfolio:
    def __init__(self, user_id):
        self._user_id = user_id
        self._wallets = {}  # словарь currency_code -Wallet

    def add_currency(self, currency_code):
        if currency_code in self._wallets:
            print(f"Кошелек {currency_code} уже есть")
            return
        self._wallets[currency_code] = Wallet(currency_code)

    def get_wallet(self, currency_code):
        return self._wallets.get(currency_code)

    def get_total_value(self, rates, base_currency="USD"):
        total = 0.0
        for code, wallet in self._wallets.items():
            rate = rates.get(code, {}).get(base_currency, 1.0)
            total += wallet.balance * rate
        return total






