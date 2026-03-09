"""
Config loading for MathMex. Single source of truth.
"""
import configparser
from pathlib import Path

from paths import get_config_path

_config = None


def get_config() -> configparser.ConfigParser:
    """Load and cache config.ini from project root."""
    global _config
    if _config is None:
        path = get_config_path()
        _config = configparser.ConfigParser()
        read = _config.read(path)
        if not read:
            raise FileNotFoundError(
                f"Config file not found: {path}\n"
                f"Copy config.ini.example to config.ini at project root."
            )
        if "general" not in _config:
            raise configparser.Error(
                f"Config missing [general] section. Check {path}"
            )
    return _config
