import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging():
    logger = logging.getLogger("wms")
    
    if logger.handlers: 
        return logger
    
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    log_directory = Path(__file__).resolve().parent.parent / "logs"
    log_directory.mkdir(parents=True, exist_ok=True)
    rotating_handler = RotatingFileHandler(
        log_directory / "wms.log",
        maxBytes=1000000,
        backupCount=3,
        encoding="utf-8",
    )
    rotating_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(rotating_handler)
    logger.propagate = False

    return logger
