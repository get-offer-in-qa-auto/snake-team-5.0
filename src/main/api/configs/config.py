import os
from pathlib import Path
from typing import Any


class Config:
    _instance = None
    _properties = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            config_path = Path(__file__).parents[4] / 'resources' / 'config.properties'
            if not config_path.exists():
                raise FileNotFoundError(f'config.properties file not found at {config_path}')
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    stripped = line.strip()
                    if stripped and not stripped.startswith('#') and '=' in stripped:
                        key, value = line.strip().split('=', 1)
                        cls._properties[key] = value
        return cls._instance

    @staticmethod
    def get(key: str, default_value: Any = None) -> Any:
        return os.getenv(key, Config()._properties.get(key, default_value))


