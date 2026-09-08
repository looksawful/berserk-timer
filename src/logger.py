import glob
import logging
import os
import sys
from datetime import datetime

LOG_DIR = "logs"
LOG_READY = True

try:
    os.makedirs(LOG_DIR, exist_ok=True)
    logging.basicConfig(
        filename=os.path.join(LOG_DIR, "berserk.log"),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
except Exception:
    LOG_READY = False
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    sys.stderr.write(
        "[berserk-timer] Logging directory unavailable. Falling back to stderr; "
        "witness logs will not be saved.\n"
    )


def log_event(message: str) -> None:
    if LOG_READY:
        logging.info(message)
    else:
        sys.stderr.write(f"[berserk-timer] {message}\n")


def log_witness_response(response: str) -> None:
    if not LOG_READY:
        sys.stderr.write(f"[berserk-timer witness] {response}\n")
        return
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(LOG_DIR, f"witness_log_{date_str}.txt")
    with open(filename, "a", encoding="utf-8") as file:
        timestamp = datetime.now().strftime("%H:%M:%S")
        file.write(f"[{timestamp}] {response}\n")


def log_timer_start(duration_minutes: float, goal: str | None = None) -> None:
    if not LOG_READY:
        sys.stderr.write(
            f"[berserk-timer witness] Timer started: {duration_minutes:.1f} minutes"
            + (f" (Goal: {goal})" if goal else "")
            + "\n"
        )
        return
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(LOG_DIR, f"witness_log_{date_str}.txt")
    with open(filename, "a", encoding="utf-8") as file:
        timestamp = datetime.now().strftime("%H:%M:%S")
        goal_str = f" (Goal: {goal})" if goal else ""
        file.write(
            f"[{timestamp}] Timer started: {duration_minutes:.1f} minutes{goal_str}\n"
        )


def log_timer_end() -> None:
    if not LOG_READY:
        sys.stderr.write("[berserk-timer witness] Timer completed\n")
        return
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(LOG_DIR, f"witness_log_{date_str}.txt")
    with open(filename, "a", encoding="utf-8") as file:
        timestamp = datetime.now().strftime("%H:%M:%S")
        file.write(f"[{timestamp}] Timer completed\n")


def view_today_log() -> str:
    if not LOG_READY:
        return "Logging is unavailable (read-only fallback active)."
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(LOG_DIR, f"witness_log_{date_str}.txt")
    if not os.path.exists(filename):
        return "No log for today."

    with open(filename, encoding="utf-8") as file:
        content = file.read()

    header = f"=== Witness Log for {date_str} ==="
    return f"{header}\n{content}"


def delete_today_log() -> None:
    if not LOG_READY:
        print("Logging unavailable; no files to delete.")
        return
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(LOG_DIR, f"witness_log_{date_str}.txt")
    if os.path.exists(filename):
        try:
            os.remove(filename)
            print(f"Today's witness log deleted: {filename}")
        except OSError as exc:
            print(f"Error deleting today's log {filename}: {exc}")
    else:
        print("No log for today to delete.")


def delete_all_logs() -> None:
    logging.shutdown()
    files = [os.path.join(LOG_DIR, "berserk.log"), *glob.glob(
        os.path.join(LOG_DIR, "witness_log_*.txt")
    )]
    for file in files:
        if os.path.exists(file):
            try:
                os.remove(file)
            except OSError as exc:
                print(f"Error deleting file {file}: {exc}")
