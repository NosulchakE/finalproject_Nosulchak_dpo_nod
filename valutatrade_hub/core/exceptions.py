class InsufficientFundsError(Exception):
    """Ошибка: недостаточно средств"""

    def __init__(self, available: float, required: float, code: str):
        message = f"Недостаточно средств: доступно {available:.4f} {code}, требуется {required:.4f} {code}"
        super().__init__(message)


class CurrencyNotFoundError(Exception):
    """Ошибка: неизвестная валюта"""

    def __init__(self, code: str):
        message = f"Неизвестная валюта '{code}'"
        super().__init__(message)


class ApiRequestError(Exception):
    """Ошибка обращения к внешнему API"""

    def __init__(self, reason: str):
        message = f"Ошибка при обращении к внешнему API: {reason}"
        super().__init__(message)
