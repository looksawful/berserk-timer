import glob
import logging
import os
import sys
from datetime import datetime
from pathlib import Path


def get_default_log_dir() -> Path:
    override = os.environ.get("BERSERK_LOG_DIR")
    if override:
        return Path(override)

    if sys.platform.startswith("win"):
        base = Path(
            os.environ.get("LOCALAPPDATA")
            or os.environ.get("APPDATA")
            or Path.home() / "AppData" / "Local"
        )
        return base / "Berserk Timer" / "logs"

    if sys.platform.startswith("darwin"):
        return (
            Path.home()
            / "Library"
            / "Application Support"
            / "Berserk Timer"
            / "logs"
        )

    xdg_state_home = os.environ.get("XDG_STATE_HOME")
    base = Path(xdg_state_home) if xdg_state_home else Path.home() / ".local" / "state"
    return base / "berserk-timer" / "logs"


LOG_DIR = get_default_log_dir()
LOG_READY = True

try:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=str(LOG_DIR / "berserk.log"),
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


def _today_witness_log_path() -> Path:
    date_str = datetime.now().strftime("%Y-%m-%d")
    return LOG_DIR / f"witness_log_{date_str}.txt"


def log_witness_response(response: str) -> None:
    if not LOG_READY:
        sys.stderr.write(f"[berserk-timer witness] {response}\n")
        return
    filename = _today_witness_log_path()
    with filename.open("a", encoding="utf-8") as file:
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
    filename = _today_witness_log_path()
    with filename.open("a", encoding="utf-8") as file:
        timestamp = datetime.now().strftime("%H:%M:%S")
        goal_str = f" (Goal: {goal})" if goal else ""
        file.write(
            f"[{timestamp}] Timer started: {duration_minutes:.1f} minutes{goal_str}\n"
        )


def log_timer_end() -> None:
    if not LOG_READY:
        sys.stderr.write("[berserk-timer witness] Timer completed\n")
        return
    filename = _today_witness_log_path()
    with filename.open("a", encoding="utf-8") as file:
        timestamp = datetime.now().strftime("%H:%M:%S")
        file.write(f"[{timestamp}] Timer completed\n")


def view_today_log() -> str:
    if not LOG_READY:
        return "Logging is unavailable (read-only fallback active)."
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = _today_witness_log_path()
    if not filename.exists():
        return "No log for today."

    with filename.open(encoding="utf-8") as file:
        content = file.read()

    header = f"=== Witness Log for {date_str} ==="
    return f"{header}\n{content}"


def delete_today_log() -> None:
    if not LOG_READY:
        print("Logging unavailable; no files to delete.")
        return
    filename = _today_witness_log_path()
    if filename.exists():
        try:
            filename.unlink()
            print(f"Today's witness log deleted: {filename}")
        except OSError as exc:
            print(f"Error deleting today's log {filename}: {exc}")
    else:
        print("No log for today to delete.")


def delete_all_logs() -> None:
    logging.shutdown()
    files = [
        str(LOG_DIR / "berserk.log"),
        *glob.glob(str(LOG_DIR / "witness_log_*.txt")),
    ]
    for file in files:
        if os.path.exists(file):
            try:
                os.remove(file)
            except OSError as exc:
                print(f"Error deleting file {file}: {exc}")
