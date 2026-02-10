import hashlib, secrets, datetime

class User:
    """Пользователь системы"""

    def __init__(self, user_id, username, password):
        self._user_id = user_id
        if not username:
            raise ValueError("Имя не может быть пустым")
        self._username = username

        # генерируем соль, чтобы одинаковые пароли не выглядели одинаково
        self._salt = secrets.token_hex(8)
        self._hashed_password = hashlib.sha256((password + self._salt).encode()).hexdigest()

        self._registration_date = datetime.datetime.now()

    def get_user_info(self):
        # возвращаем информацию о пользователе без пароля
        return {
            "user_id": self._user_id,
            "username": self._username,
            "registration_date": self._registration_date.isoformat()
        }

    def change_password(self, new_password):
        if len(new_password) < 4:
            raise ValueError("Пароль слишком короткий")
        # меняем пароль, новая соль для каждого изменения (ТЗ??)
        self._salt = secrets.token_hex(8)
        self._hashed_password = hashlib.sha256((new_password + self._salt).encode()).hexdigest()

    def verify_password(self, password):
        return self._hashed_password == hashlib.sha256((password + self._salt).encode()).hexdigest()



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





