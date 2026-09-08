import os
import subprocess
import sys
import threading
import time
from pathlib import Path

_sound_playing = False
_sound_start_time = 0.0
_sound_duration = 0.0
_sound_name = ""
_global_mute = False
_sound_process: subprocess.Popen[bytes] | None = None
_playback_generation = 0
_state_lock = threading.Lock()


def get_sound_duration(sound_path: str) -> float:
    try:
        import wave

        with wave.open(sound_path, "r") as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            return frames / float(rate)
    except Exception:
        return 0.0


def is_sound_playing() -> bool:
    with _state_lock:
        return _sound_playing


def is_globally_muted() -> bool:
    with _state_lock:
        return _global_mute


def get_sound_remaining() -> tuple[int, int, str]:
    global _sound_playing
    with _state_lock:
        if not _sound_playing:
            return (0, 0, "")
        elapsed = time.monotonic() - _sound_start_time
        remaining = max(0.0, _sound_duration - elapsed)
        if remaining <= 0:
            _sound_playing = False
        return (int(remaining), int(_sound_duration), _sound_name)


def _source_assets_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "assets"


def _installed_assets_dir() -> Path:
    return Path(sys.prefix) / "share" / "berserk-timer" / "assets"


def get_available_sounds() -> list[str]:
    for assets_dir in (_source_assets_dir(), _installed_assets_dir()):
        if assets_dir.is_dir():
            return sorted(path.name for path in assets_dir.glob("*.wav"))
    return []


def get_sound_path(sound_filename: str) -> str:
    for assets_dir in (_source_assets_dir(), _installed_assets_dir()):
        candidate = assets_dir / sound_filename
        if candidate.exists():
            return str(candidate)
    return str(_source_assets_dir() / sound_filename)


def _play_with_pygame(asset_path: str, volume: float, duration: int | None) -> bool:
    try:
        os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
        import pygame

        pygame.mixer.init()
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.load(asset_path)
        pygame.mixer.music.play()
        if duration is not None:
            time.sleep(duration)
            pygame.mixer.music.stop()
        else:
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        return True
    except Exception:
        return False


def _play_native(
    asset_path: str,
    volume: float,
    duration: int | None,
) -> None:
    global _sound_process

    if sys.platform.startswith("win"):
        try:
            import winsound

            winsound.PlaySound(asset_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            if duration is not None:
                time.sleep(duration)
                winsound.PlaySound(None, winsound.SND_PURGE)
        except Exception as exc:
            print(f"Error playing sound on Windows: {exc}")
            print("\a", end="", flush=True)
        return

    if sys.platform.startswith("linux"):
        command = ["aplay", "-q", asset_path]
    elif sys.platform.startswith("darwin"):
        command = ["afplay", "-v", str(volume), asset_path]
    else:
        print("\a", end="", flush=True)
        return

    process: subprocess.Popen[bytes] | None = None
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        with _state_lock:
            _sound_process = process
        if duration is None:
            process.wait()
        else:
            try:
                process.wait(timeout=duration)
            except subprocess.TimeoutExpired:
                _terminate_process(process)
    except (OSError, subprocess.SubprocessError) as exc:
        platform_name = "Linux" if sys.platform.startswith("linux") else "macOS"
        print(f"Error playing sound on {platform_name}: {exc}")
        print("\a", end="", flush=True)
    finally:
        with _state_lock:
            if _sound_process is process:
                _sound_process = None


def play_sound(
    sound_filename: str = "alert1.wav",
    volume: int = 5,
    duration: int | None = None,
) -> None:
    global _sound_playing, _sound_start_time, _sound_duration, _sound_name
    global _playback_generation

    if is_globally_muted():
        return

    if is_sound_playing():
        stop_sound()

    asset_path = get_sound_path(sound_filename)
    if not os.path.exists(asset_path):
        print(f"Sound file not found: {asset_path}")
        print("\a", end="", flush=True)
        return

    file_duration = get_sound_duration(asset_path)
    actual_duration = float(duration) if duration is not None else file_duration
    normalized_volume = max(0, min(10, volume)) / 10

    with _state_lock:
        _playback_generation += 1
        generation = _playback_generation
        _sound_playing = True
        _sound_start_time = time.monotonic()
        _sound_duration = actual_duration
        _sound_name = sound_filename

    def play_thread() -> None:
        global _sound_playing
        try:
            if not _play_with_pygame(asset_path, normalized_volume, duration):
                _play_native(asset_path, normalized_volume, duration)
        finally:
            with _state_lock:
                if generation == _playback_generation:
                    _sound_playing = False

    threading.Thread(target=play_thread, daemon=True).start()


def _terminate_process(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=1)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=1)


def _terminate_owned_process() -> None:
    with _state_lock:
        process = _sound_process
    if process is not None:
        _terminate_process(process)


def stop_sound() -> None:
    global _sound_playing, _playback_generation

    with _state_lock:
        _playback_generation += 1
        _sound_playing = False

    try:
        import pygame

        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
    except Exception:
        pass

    if sys.platform.startswith("win"):
        try:
            import winsound

            winsound.PlaySound(None, winsound.SND_PURGE)
        except Exception:
            pass

    try:
        _terminate_owned_process()
    except (OSError, subprocess.SubprocessError):
        pass


def set_mute(mute: bool) -> None:
    global _global_mute
    with _state_lock:
        _global_mute = bool(mute)
        should_stop = _global_mute and _sound_playing
    if should_stop:
        stop_sound()
