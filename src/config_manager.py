# config_manager.py
import json
import os
DEFAULT_CONFIG = {
    "messages": [
        "Drink water",
        "Do push-ups",
        "Take a short walk",
        "Stretch your legs",
        "Take a breath",
        "Take a break",
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
    "witness_mode": False
}


def load_config(config_path="config.json"):
    if not os.path.exists(config_path):
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)
