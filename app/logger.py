import logging
from logging.handlers import RotatingFileHandler

def setup_logger():
    """
    Set up a logger that logs to both console and file.
    """
    logger = logging.getLogger("concert-app-logger")
    logger.setLevel(logging.DEBUG)

    c_handler = logging.StreamHandler()
    f_handler = RotatingFileHandler('concert-app.log', maxBytes=1_000_000, backupCount=5)
    c_handler.setLevel(logging.INFO)
    f_handler.setLevel(logging.DEBUG)

    # Create formatters and add it to handlers
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(log_format, datefmt=date_format)

    c_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger
