import logging, os, sys

from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Iterable

from conf import Settings


def configure_task_logger(name: str, log_dir: Path):
    """
    Setting up logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_dir = os.path.join(log_dir, 'logs')

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file_path = os.path.join(log_dir, f'{name}.log')

    file_handler = RotatingFileHandler(
        log_file_path, maxBytes=100000, backupCount=1
    )
    stdout_handler = logging.StreamHandler(sys.stdout)

    stdout_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)

    return logger


def write_to_file(filename: str, data: list):
    with open(filename, 'a+', encoding='utf-8') as d:
        last_row = d.read().split('\n')[-1]
        if last_row != data[-1]:
            d.write('\n')
            d.write('\n'.join(data))
