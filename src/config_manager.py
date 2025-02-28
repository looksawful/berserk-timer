"""Module config_manager.py: Handles configuration loading and saving for the Berserk Timer application."""
import json
import os
from typing import Any, Dict

DEFAULT_CONFIG: Dict[str, Any] = {
    "messages": [
        "Drink water",
        "Do push-ups",
        "Take a short walk",
        "Stretch your legs",
        "Take a breath",
        "Take a break",
        "Drink tea",
        "Read a few pages"
    ],
    "presets": {
        "xs": 5,
        "s": 10,
        "m": 15,
        "l": 20,
        "xl": 25,
        "test": 0.1
    },
    "witness_mode": True,
}


def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Loads the configuration from a JSON file or creates a default one if not existent.
    Args:
        config_path (str): Path to the configuration file.
    Returns:
        Dict[str, Any]: Configuration dictionary.
    """
    if not os.path.exists(config_path):
    if not os.path.exists(config_path):
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG.copy()
    else:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
