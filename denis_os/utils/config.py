"""
Configuration Manager for DenisOS
"""

import json
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = {
    "app": {
        "name": "DenisOS",
        "version": "1.1.0",
        "theme": "notebook"
    },
    "user": {
        "name": "Denis",
        "timezone": "America/Toronto",
        "currency": "CAD",
        "units": "imperial"
    },
    "api": {
        "anthropic_key": ""
    },
    "modules": {
        "finance": {"enabled": True, "default_currency": "CAD"},
        "carpentry": {"enabled": True, "default_units": "imperial", "waste_factor": 1.10},
        "philosophy": {"enabled": True, "daily_reflection_reminder": True}
    },
    "display": {
        "date_format": "%B %d, %Y",
        "time_format": "%I:%M %p",
        "entries_per_page": 10
    }
}


def get_config_path() -> Path:
    """Get the path to the config file."""
    return Path(__file__).parent.parent / "config.json"


def load_config() -> dict:
    """Load configuration from file or return defaults."""
    config_path = get_config_path()

    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            return _merge_configs(DEFAULT_CONFIG, user_config)
        except (json.JSONDecodeError, IOError):
            pass

    save_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG.copy()


def save_config(config: dict) -> bool:
    """Save configuration to file."""
    config_path = get_config_path()
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        return True
    except IOError:
        return False


def get_config_value(key_path: str, default: Any = None) -> Any:
    """Get a nested config value using dot notation."""
    config = load_config()
    keys = key_path.split('.')

    value = config
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    return value


def set_config_value(key_path: str, value: Any) -> bool:
    """Set a nested config value using dot notation."""
    config = load_config()
    keys = key_path.split('.')

    current = config
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]

    current[keys[-1]] = value
    return save_config(config)


def _merge_configs(default: dict, user: dict) -> dict:
    """Deep merge user config with defaults."""
    result = default.copy()

    for key, value in user.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_configs(result[key], value)
        else:
            result[key] = value

    return result
