import logging
import os
import glob
from datetime import datetime
import sys
import subprocess
from typing import Optional

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
        "[berserk-timer] Logging directory unavailable. Falling back to stderr; witness logs will not be saved.\n"
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
    with open(filename, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%H:%M:%S")
        f.write(f"[{timestamp}] {response}\n")


def log_timer_start(duration_minutes: float, goal: str = None) -> None:
    if not LOG_READY:
        sys.stderr.write(
            f"[berserk-timer witness] Timer started: {duration_minutes:.1f} minutes"
            + (f" (Goal: {goal})" if goal else "")
            + "\n"
        )
        return
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(LOG_DIR, f"witness_log_{date_str}.txt")
    with open(filename, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%H:%M:%S")
        goal_str = f" (Goal: {goal})" if goal else ""
        f.write(
            f"[{timestamp}] Timer started: {duration_minutes:.1f} minutes{goal_str}\n"
        )


def log_timer_end() -> None:
    if not LOG_READY:
        sys.stderr.write("[berserk-timer witness] Timer completed\n")
        return
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(LOG_DIR, f"witness_log_{date_str}.txt")
    with open(filename, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%H:%M:%S")
        f.write(f"[{timestamp}] Timer completed\n")


def view_today_log() -> str:
    if not LOG_READY:
        return "Logging is unavailable (read-only fallback active)."
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(LOG_DIR, f"witness_log_{date_str}.txt")
    if not os.path.exists(filename):
        return "No log for today."

    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

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
        except Exception as e:
            print(f"Error deleting today's log {filename}: {e}")
    else:
        print("No log for today to delete.")


def delete_all_logs() -> None:
    logging.shutdown()
    files = [os.path.join(LOG_DIR, "berserk.log")] + glob.glob(
        os.path.join(LOG_DIR, "witness_log_*.txt")
    )
    for file in files:
        if os.path.exists(file):
            try:
                os.remove(file)
            except Exception as e:
                print(f"Error deleting file {file}: {e}")


_sound_playing = False
_sound_start_time = 0
_sound_duration = 0
_sound_name = ""
_global_mute = False


def get_sound_duration(sound_path: str) -> float:
    try:
        import wave

        with wave.open(sound_path, "r") as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            duration = frames / float(rate)
            return duration
    except Exception:
        return 0


def is_sound_playing() -> bool:
    return _sound_playing


def is_globally_muted() -> bool:
    return _global_mute


def get_sound_remaining() -> tuple:
    global _sound_playing, _sound_start_time, _sound_duration, _sound_name
    if not _sound_playing:
        return (0, 0, "")

    import time

    elapsed = time.time() - _sound_start_time
    remaining = max(0, _sound_duration - elapsed)

    if remaining <= 0:
        _sound_playing = False

    return (int(remaining), int(_sound_duration), _sound_name)


def get_available_sounds() -> list:
    assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
    assets_dir = os.path.abspath(assets_dir)
    if not os.path.exists(assets_dir):
        return []

    sound_files = []
    for file in os.listdir(assets_dir):
        if file.endswith(".wav"):
            sound_files.append(file)
    return sorted(sound_files)


def get_sound_path(sound_filename: str) -> str:
    asset_path = os.path.join(os.path.dirname(__file__), "..", "assets", sound_filename)
    return os.path.abspath(asset_path)


def play_sound(
    sound_filename: str = "alert1.wav", volume: int = 5, duration: Optional[int] = None
) -> None:
    import threading
    import time

    global _sound_playing, _sound_start_time, _sound_duration, _sound_name

    if _global_mute or not LOG_READY:
        return

    asset_path = get_sound_path(sound_filename)
    if not os.path.exists(asset_path):
        print(f"Sound file not found: {asset_path}")
        print("\a", end="", flush=True)
        return

    file_duration = get_sound_duration(asset_path)
    actual_duration = duration if duration else file_duration

    _sound_playing = True
    _sound_start_time = time.time()
    _sound_duration = actual_duration
    _sound_name = sound_filename

    volume_percent = volume * 10

    def play_thread():
        if sys.platform.startswith("win"):
            try:
                try:
                    import os

                    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
                    import pygame

                    pygame.mixer.init()
                    pygame.mixer.music.set_volume(volume_percent / 100)
                    pygame.mixer.music.load(asset_path)
                    pygame.mixer.music.play()
                    if duration:
                        time_module = __import__("time")
                        time_module.sleep(duration)
                        pygame.mixer.music.stop()
                    else:
                        while pygame.mixer.music.get_busy():
                            time_module = __import__("time")
                            time_module.sleep(0.1)
                except ImportError:
                    import winsound

                    winsound.PlaySound(
                        asset_path, winsound.SND_FILENAME | winsound.SND_ASYNC
                    )
                    if duration:
                        time_module = __import__("time")
                        time_module.sleep(duration)
                        winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception as e:
                print(f"Error playing sound on Windows: {e}")
                print("\a", end="", flush=True)
        elif sys.platform.startswith("linux"):
            try:
                subprocess.run(
                    ["amixer", "-q", "sset", "Master", f"{volume_percent}%"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                cmd = ["aplay", "-q", asset_path]
                if duration:
                    cmd = ["timeout", str(duration)] + cmd
                subprocess.run(
                    cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            except Exception as e:
                print(f"Error playing sound on Linux: {e}")
                print("\a", end="", flush=True)
        elif sys.platform.startswith("darwin"):
            try:
                cmd = ["afplay", "-v", str(volume_percent / 100), asset_path]
                if duration:
                    import signal

                    proc = subprocess.Popen(
                        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )
                    try:
                        proc.wait(timeout=duration)
                    except subprocess.TimeoutExpired:
                        proc.terminate()
                        proc.wait()
                else:
                    subprocess.run(
                        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )
            except Exception as e:
                print(f"Error playing sound on macOS: {e}")
                print("\a", end="", flush=True)
        else:
            print("\a", end="", flush=True)

        global _sound_playing
        _sound_playing = False

    thread = threading.Thread(target=play_thread, daemon=True)
    thread.start()


def stop_sound() -> None:
    global _sound_playing
    try:
        if sys.platform.startswith("win"):
            try:
                import pygame

                if pygame.mixer.get_init():
                    pygame.mixer.music.stop()
            except (ImportError, pygame.error):
                import winsound

                winsound.PlaySound(None, winsound.SND_PURGE)
        elif sys.platform.startswith("linux"):
            subprocess.run(["killall", "-q", "aplay"], stderr=subprocess.DEVNULL)
        elif sys.platform.startswith("darwin"):
            subprocess.run(["killall", "-q", "afplay"], stderr=subprocess.DEVNULL)
    except Exception:
        pass
    finally:
        _sound_playing = False


def set_mute(mute: bool) -> None:
    global _global_mute
    _global_mute = bool(mute)
    if _global_mute and is_sound_playing():
        stop_sound()
