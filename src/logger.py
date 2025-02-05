import winsound
import logging
from datetime import datetime
import os
import glob

LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "berserk.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def log_event(message):
    logging.info(message)

# TODO use log or json instead of txt?


def log_witness_response(response):
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(LOG_DIR, f"witness_log_{date_str}.txt")
    with open(filename, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%H:%M:%S")
        f.write(f"[{timestamp}] {response}\n")

# TODO possibility to wake the logs without running the timer


def view_today_log():
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(LOG_DIR, f"witness_log_{date_str}.txt")
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return "No log for today."


def delete_all_logs():
    logging.shutdown()

    files = [os.path.join(LOG_DIR, "berserk.log")] + \
        glob.glob(os.path.join(LOG_DIR, "witness_log_*.txt"))
    for file in files:
        if os.path.exists(file):
            try:
                os.remove(file)
            except Exception as e:
                print(f"Error deleting file {file}: {e}")


def play_sound():
    winsound.Beep(1000, 500)
