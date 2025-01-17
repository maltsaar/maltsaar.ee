import logging
from .log import create_logger
from .core import create_website
from pathlib import Path
import shutil
from os import environ
from .configuration import OUTPUT_DIRECTORY

def main() -> None:
    create_logger()
    log = logging.getLogger("create-website")
    create_website()

def clean() -> None:
    log_file = environ.get("LOG_FILE", "create-website.log")
    Path.unlink(Path(log_file))
    shutil.rmtree(OUTPUT_DIRECTORY)
