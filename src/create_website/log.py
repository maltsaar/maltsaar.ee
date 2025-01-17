import logging
from os import environ

def create_logger() -> None:
    log = logging.getLogger("create-website")
    log_level = environ.get("LOG_LEVEL", "INFO").upper()
    log.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # File handler
    log_file = environ.get("LOG_FILE", "create-website.log")
    file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    file_handler.setLevel(log_level)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)-8s - %(message)s")
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    log.addHandler(console_handler)
    log.addHandler(file_handler)
