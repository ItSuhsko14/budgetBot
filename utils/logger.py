import logging

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    return logger

logger = setup_logger()
