# valutatrade_hub/core/models.py
import hashlib
import os
from typing import List, Optional


class User:
    def __init__(self, user_id: int, username: str, password: str, salt: Optional[str] = None):
        self.user_id = user_id
        self.username = username
        self.salt = salt or os.urandom(16).hex()
        self.password_hash = self._hash_password(password)

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256((password + self.salt).encode("utf-8")).hexdigest()

    def verify_password(self, password: str) -> bool:
        return self.password_hash == hashlib.sha256((password + self.salt).encode("utf-8")).hexdigest()

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "salt": self.salt,
            "password_hash": self.password_hash
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls(data["user_id"], data["username"], "")
        obj.salt = data["salt"]
        obj.password_hash = data["password_hash"]
        return obj


class Wallet:
    def __init__(self, currency: str, balance: float = 0.0):
        self.currency = currency.upper()
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    def deposit(self, amount: float):
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")
        self._balance += amount

    def withdraw(self, amount: float):
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")
        if amount > self._balance:
            raise ValueError("Недостаточно средств")
        self._balance -= amount

    def to_dict(self):
        return {"currency": self.currency, "balance": self._balance}

    @classmethod
    def from_dict(cls, data):
        return cls(data["currency"], data["balance"])


class Portfolio:
    def __init__(self, user_id: int, wallets: Optional[List[Wallet]] = None):
        self.user_id = user_id
        self.wallets = wallets or []

    def get_wallet(self, currency: str) -> Wallet:
        currency = currency.upper()
        for w in self.wallets:
            if w.currency == currency:
                return w
        # если кошелек отсутствует — создаём новый
        new_wallet = Wallet(currency)
        self.wallets.append(new_wallet)
        return new_wallet

    def get_total_value(self, base: str = "USD", rates: dict = None) -> float:
        total = 0.0
        base = base.upper()
        rates = rates or {}
        for wallet in self.wallets:
            pair_key = f"{wallet.currency}{base}"
            rate = rates.get(pair_key, {"rate": 1.0})["rate"] if wallet.currency != base else 1.0
            total += wallet.balance * rate
        return total

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "wallets": [w.to_dict() for w in self.wallets]
        }

    @classmethod
    def from_dict(cls, data):
        wallets = [Wallet.from_dict(w) for w in data.get("wallets", [])]
        return cls(data["user_id"], wallets)


# ---- Утилиты для работы с пользователями и портфелями ----

def get_user_by_username(username: str, users_list: Optional[list] = None) -> Optional[User]:
    users_list = users_list or []
    for u in users_list:
        if u["username"] == username:
            return User.from_dict(u)
    return None


def save_users(users_list: list, file_path: str):
    import json, os
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(users_list, f, ensure_ascii=False, indent=2)


def save_portfolios(portfolios_list: list, file_path: str):
    import json, os
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump([p.to_dict() if isinstance(p, Portfolio) else p for p in portfolios_list], f, ensure_ascii=False, indent=2)


