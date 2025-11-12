from dataclasses import dataclass
import hashlib
import uuid

@dataclass
class User:
    username: str
    password_hash: str
    user_id: str = None

    def __post_init__(self):
        if not self.user_id:
            self.user_id = str(uuid.uuid4())

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password: str) -> bool:
        return self.password_hash == self.hash_password(password)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(username=data["username"], password_hash=data["password_hash"], user_id=data["user_id"])

    def to_dict(self):
        return {"username": self.username, "password_hash": self.password_hash, "user_id": self.user_id}

@dataclass
class Wallet:
    currency: str
    balance: float = 0.0

@dataclass
class Portfolio:
    user_id: str
    wallets: list[Wallet]




