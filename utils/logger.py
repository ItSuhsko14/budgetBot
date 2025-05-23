import logging
import sys

class BudgetFormatter(logging.Formatter):
    def format(self, record):
        record.msg = f"[budget] {record.msg}"
        return super().format(record)

def setup_budget_logger():
    logger = logging.getLogger("budget")  # створює окремий логер
    logger.setLevel(logging.INFO)

    # Перевіряємо, чи ще не додано хендлер
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = BudgetFormatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.propagate = False
    return logger

# Ініціалізуємо логер і створюємо зручне імʼя log
_log = setup_budget_logger()
log = _log.info  # Тепер просто log("повідомлення")