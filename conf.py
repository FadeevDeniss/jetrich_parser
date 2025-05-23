import os

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    username: str = os.getenv('USERNAME')
    password: str = os.getenv('PASSWORD')
    BASE_DIR: Path = Path(__file__).resolve().parent
