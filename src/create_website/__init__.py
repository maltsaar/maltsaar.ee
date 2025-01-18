import logging
from create_website.log import create_logger
from create_website.core import create_website
from pathlib import Path
import shutil
from os import environ
from create_website.configuration import OUTPUT_DIRECTORY

def main() -> None:
    create_logger()
    log = logging.getLogger("create-website")
    create_website()

def clean() -> None:
    log_file = environ.get("LOG_FILE", "create-website.log")
    Path.unlink(Path(log_file))
    shutil.rmtree(OUTPUT_DIRECTORY)
