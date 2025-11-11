# valutatrade_hub/parser_service/scheduler.py
# Можно использовать для автоматического обновления по расписанию (опционально)
import threading
import time
from .updater import RatesUpdater

class RatesScheduler:
    """Простейший планировщик обновлений"""
    def __init__(self, interval_sec=300):
        self.updater = RatesUpdater()
        self.interval = interval_sec
        self._thread = threading.Thread(target=self._run_loop, daemon=True)

    def start(self):
        self._thread.start()

    def _run_loop(self):
        while True:
            try:
                self.updater.run_update()
            except Exception:
                pass  # ошибки логируются внутри updater
            time.sleep(self.interval)
