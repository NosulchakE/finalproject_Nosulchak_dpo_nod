# valutatrade_hub/parser_service/__init__.py
from .updater import RatesUpdater, MockRatesUpdater

__all__ = ['RatesUpdater', 'MockRatesUpdater']
