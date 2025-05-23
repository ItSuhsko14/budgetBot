import logging
import sys

class BudgetFormatter(logging.Formatter):
    def format(self, record):
        record.msg = f"[budget] {record.msg}"
        return super().format(record)

def setup_logger():
    handler = logging.StreamHandler(sys.stdout)
    formatter = BudgetFormatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers = [handler]  # Очистити попередні хендлери і додати один

    return logger

logger = setup_logger()
