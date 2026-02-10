class InsufficientFundsError(Exception):
    """Недостаточно средств в кошельке"""

    def __init__(self, available: float, required: float, code: str):
        self.available = available
        self.required = required
        self.code = code

        message = (
            f"Недостаточно средств: "
            f"доступно {available:.4f} {code}, "
            f"требуется {required:.4f} {code}"
        )
        super().__init__(message)


class CurrencyNotFoundError(Exception):
    """Неизвестная валюта"""

    def __init__(self, code: str):
        self.code = code
        message = f"Неизвестная валюта '{code}'"
        super().__init__(message)


class ApiRequestError(Exception):
    """Ошибка при обращении к внешнему API"""

    def __init__(self, reason: str):
        self.reason = reason
        message = f"Ошибка при обращении к внешнему API: {reason}"
        super().__init__(message)



