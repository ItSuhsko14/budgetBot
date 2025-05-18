import logging
import sys

def setup_logger():
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers = [handler]  # Очистити попередні хендлери і додати один

    return logger

logger = setup_logger()
