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
        "Read a few pages",
    ],
    "presets": {"xs": 5, "s": 10, "m": 15, "l": 20, "xl": 25, "test": 1},  # test preset: 1 minute
    "witness_mode": True,
    "safe_word": "skip",
    "sound_file": "alert1.wav",  # default sound file in assets/
    "volume": 5,  # volume level 0-10 (5 = 50%)
}


def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Loads the configuration from a JSON file or creates a default one if not existent.
    Args:
        config_path (str): Path to the configuration file.
    Returns:
        Dict[str, Any]: Configuration dictionary.
    """
    if not os.path.exists(config_path):
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    # Sanitize messages: remove empty or whitespace-only entries
    if "messages" in config and isinstance(config["messages"], list):
        config["messages"] = [m for m in config["messages"] if isinstance(m, str) and m.strip()]
    # Ensure safe_word present
    if "safe_word" not in config:
        config["safe_word"] = DEFAULT_CONFIG.get("safe_word", "skip")
    # Ensure sound_file present
    if "sound_file" not in config:
        config["sound_file"] = DEFAULT_CONFIG.get("sound_file", "alert1.wav")
    # Ensure volume present and valid (0-10)
    if "volume" not in config:
        config["volume"] = DEFAULT_CONFIG.get("volume", 5)
    else:
        # Validate volume range
        try:
            vol = int(config["volume"])
            config["volume"] = max(0, min(10, vol))  # Clamp to 0-10
        except (ValueError, TypeError):
            config["volume"] = 5
    return config
