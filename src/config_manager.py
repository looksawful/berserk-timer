import copy
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

DEFAULT_CONFIG: dict[str, Any] = {
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
    "presets": {"xs": 5, "s": 10, "m": 15, "l": 20, "xl": 25, "test": 1},
    "witness_mode": True,
    "safe_word": "skip",
    "sound_file": "alert1.wav",
    "volume": 5,
}


def get_default_config_path() -> Path:
    if sys.platform.startswith("win"):
        base = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
        return base / "Berserk Timer" / "config.json"
    if sys.platform.startswith("darwin"):
        return (
            Path.home()
            / "Library"
            / "Application Support"
            / "Berserk Timer"
            / "config.json"
        )
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg_config_home) if xdg_config_home else Path.home() / ".config"
    return base / "berserk-timer" / "config.json"


def get_legacy_source_config_path() -> Path:
    return Path(__file__).resolve().parent.parent / "config.json"


def load_config(config_path: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    path = Path(config_path) if config_path is not None else get_default_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        legacy_path = get_legacy_source_config_path() if config_path is None else None
        if legacy_path is not None and legacy_path.is_file() and legacy_path != path:
            shutil.copyfile(legacy_path, path)
        else:
            with path.open("w", encoding="utf-8") as file:
                json.dump(DEFAULT_CONFIG, file, indent=4)

    with path.open(encoding="utf-8") as file:
        loaded = json.load(file)

    config = copy.deepcopy(DEFAULT_CONFIG)
    if isinstance(loaded, dict):
        config.update(loaded)

    messages = config.get("messages")
    if isinstance(messages, list):
        config["messages"] = [
            message
            for message in messages
            if isinstance(message, str) and message.strip()
        ]
    else:
        config["messages"] = copy.deepcopy(DEFAULT_CONFIG["messages"])

    presets = config.get("presets")
    if not isinstance(presets, dict):
        config["presets"] = copy.deepcopy(DEFAULT_CONFIG["presets"])

    safe_word = config.get("safe_word")
    if not isinstance(safe_word, str) or not safe_word.strip():
        config["safe_word"] = DEFAULT_CONFIG["safe_word"]

    sound_file = config.get("sound_file")
    if not isinstance(sound_file, str) or not sound_file.strip():
        config["sound_file"] = DEFAULT_CONFIG["sound_file"]

    try:
        volume = int(config.get("volume", DEFAULT_CONFIG["volume"]))
        config["volume"] = max(0, min(10, volume))
    except (ValueError, TypeError):
        config["volume"] = DEFAULT_CONFIG["volume"]

    config["witness_mode"] = bool(
        config.get("witness_mode", DEFAULT_CONFIG["witness_mode"])
    )
    return config
