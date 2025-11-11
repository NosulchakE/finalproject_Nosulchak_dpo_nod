from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Type
from .exceptions import CurrencyNotFoundError


# === Абстрактный базовый класс ===
@dataclass
class Currency(ABC):
    """Абстрактный класс валюты"""
    name: str
    code: str

    def __post_init__(self):
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Имя валюты не может быть пустым")
        if not self.code.isupper() or not (2 <= len(self.code) <= 5):
            raise ValueError("Код валюты должен быть в верхнем регистре и длиной 2–5 символов")

    @abstractmethod
    def get_display_info(self) -> str:
        """Возвращает человекочитаемое описание валюты"""
        pass


# === Наследники ===
@dataclass
class FiatCurrency(Currency):
    issuing_country: str

    def get_display_info(self) -> str:
        return f"[FIAT] {self.code} — {self.name} (Issuing: {self.issuing_country})"


@dataclass
class CryptoCurrency(Currency):
    algorithm: str
    market_cap: float

    def get_display_info(self) -> str:
        return f"[CRYPTO] {self.code} — {self.name} (Algo: {self.algorithm}, MCAP: {self.market_cap:.2e})"


# === Реестр валют ===
_currency_registry: Dict[str, Currency] = {
    "USD": FiatCurrency(name="US Dollar", code="USD", issuing_country="United States"),
    "EUR": FiatCurrency(name="Euro", code="EUR", issuing_country="Eurozone"),
    "BTC": CryptoCurrency(name="Bitcoin", code="BTC", algorithm="SHA-256", market_cap=1.12e12),
    "ETH": CryptoCurrency(name="Ethereum", code="ETH", algorithm="Ethash", market_cap=4.4e11),
}


def get_currency(code: str) -> Currency:
    """Фабричный метод для получения валюты по коду"""
    code = code.strip().upper()
    if code not in _currency_registry:
        raise CurrencyNotFoundError(code)
    return _currency_registry[code]
