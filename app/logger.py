import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger():
    """
    Set up a logger that logs to both console and file.
    """
    logger = logging.getLogger("concert-app-logger")
    logger.setLevel(logging.DEBUG)

    c_handler = logging.StreamHandler()
    log_file = 'concert-app.log'
    f_handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=5)
    c_handler.setLevel(logging.INFO)
    f_handler.setLevel(logging.DEBUG)

    # Create formatters and add it to handlersdhjasdgsaj
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(log_format, datefmt=date_format)

    c_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    if not os.path.exists(log_file):
        with open(log_file, 'w'):
            pass
    os.chmod(log_file, 0o666)

    return logger
