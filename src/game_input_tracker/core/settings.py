from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from platformdirs import user_config_dir, user_data_dir


APP_NAME = "KeyPulse"
APP_AUTHOR = "KeyPulse"


@dataclass(frozen=True)
class AppPaths:
    data_dir: Path
    config_dir: Path
    database_path: Path


def get_app_paths() -> AppPaths:
    data_dir = Path(user_data_dir(APP_NAME, APP_AUTHOR))
    config_dir = Path(user_config_dir(APP_NAME, APP_AUTHOR))
    data_dir.mkdir(parents=True, exist_ok=True)
    config_dir.mkdir(parents=True, exist_ok=True)
    return AppPaths(
        data_dir=data_dir,
        config_dir=config_dir,
        database_path=data_dir / "keypulse.sqlite3",
    )
