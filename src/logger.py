import logging
import os
import glob
from datetime import datetime
import sys
import subprocess
from typing import Optional

LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "berserk.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def log_event(message: str) -> None:
    logging.info(message)


def log_witness_response(response: str) -> None:
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(LOG_DIR, f"witness_log_{date_str}.txt")
    with open(filename, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%H:%M:%S")
        f.write(f"[{timestamp}] {response}\n")


def view_today_log() -> str:
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(LOG_DIR, f"witness_log_{date_str}.txt")
    return open(filename, "r", encoding="utf-8").read() if os.path.exists(filename) else "No log for today."


def delete_all_logs() -> None:
    logging.shutdown()
    files = [os.path.join(LOG_DIR, "berserk.log")] + \
        glob.glob(os.path.join(LOG_DIR, "witness_log_*.txt"))
    for file in files:
        if os.path.exists(file):
            try:
                os.remove(file)
            except Exception as e:
                print(f"Error deleting file {file}: {e}")


def play_sound() -> None:
    asset_path = os.path.join(os.path.dirname(
        __file__), "..", "assets", "sound.wav")
    asset_path = os.path.abspath(asset_path)
    if not os.path.exists(asset_path):
        print(f"Sound file not found: {asset_path}")
        return
    if sys.platform.startswith("win"):
        try:
            import winsound
            winsound.PlaySound(asset_path, winsound.SND_FILENAME)
        except Exception as e:
            print(f"Error playing sound on Windows: {e}")
    elif sys.platform.startswith("linux"):
        try:
            subprocess.run(["aplay", asset_path], check=True)
        except Exception as e:
            print(f"Error playing sound on Linux: {e}")
            print('\a', end='', flush=True)
    elif sys.platform.startswith("darwin"):
        try:
            subprocess.run(["afplay", asset_path], check=True)
        except Exception as e:
            print(f"Error playing sound on macOS: {e}")
            print('\a', end='', flush=True)
    else:
        print('\a', end='', flush=True)


def set_mute(mute: bool) -> None:
    if mute:
        print("Sound is off.")
    else:
        print("Sound is on.")
