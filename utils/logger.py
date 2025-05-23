import logging
import sys

class BudgetFormatter(logging.Formatter):
    def format(self, record):
        record.msg = f"[budget] {record.msg}"
        return super().format(record)

def setup_budget_logger():
    handler = logging.StreamHandler(sys.stdout)
    formatter = BudgetFormatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger("budget")
    logger.setLevel(logging.INFO)
    logger.handlers = [handler]
    logger.propagate = False  # Важливо: щоб не дублювати в root

    return logger

# Ініціалізуємо логер і створюємо зручне імʼя log
_log = setup_budget_logger()
log = _log.info  # Тепер просто log("повідомлення")