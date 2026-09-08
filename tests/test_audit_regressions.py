import sys
import threading

import pytest

import src.audio as audio
import src.logger as logger
import src.main as main
import src.screen_manager as screen_manager
import src.timer as timer_module
from src.timer import Timer


def test_timer_elapsed_time_is_not_affected_by_wall_clock_jumps(monkeypatch):
    timer = Timer(duration=1.0)
    wall_times = iter([100.0, 90.0, 80.0])
    sleeps = 0

    monkeypatch.setattr(timer_module.time, "time", lambda: next(wall_times))

    def fake_sleep(_seconds):
        nonlocal sleeps
        sleeps += 1
        if sleeps >= 2:
            timer._stop_event.set()

    monkeypatch.setattr(timer_module.time, "sleep", fake_sleep)

    timer._run()

    assert timer.get_remaining_time() <= timer.duration


def test_unknown_cli_arguments_are_rejected(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["berserk", "5", "--definitely-not-a-real-flag"])

    with pytest.raises(SystemExit):
        main.parse_arguments()


def test_explicit_zero_duration_is_not_treated_as_interactive(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["berserk", "0"])
    monkeypatch.setattr(main, "init_screen", lambda **_kwargs: None)
    monkeypatch.setattr(main.atexit, "register", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(main, "cleanup_screen", lambda: None)
    monkeypatch.setattr(main, "load_config", lambda: {"presets": {}, "witness_mode": False})

    def unexpected_input(_prompt=""):
        raise AssertionError("explicit zero duration must be validated, not prompt interactively")

    monkeypatch.setattr("builtins.input", unexpected_input)

    with pytest.raises(SystemExit):
        main.main()


def test_audio_playback_is_not_disabled_when_file_logging_is_unavailable(
    monkeypatch, tmp_path
):
    sound = tmp_path / "alert.wav"
    sound.write_bytes(b"not-a-real-wave")
    started = []

    class FakeThread:
        def __init__(self, target, daemon=False):
            self.target = target
            self.daemon = daemon

        def start(self):
            started.append(True)

    monkeypatch.setattr(logger, "LOG_READY", False)
    monkeypatch.setattr(audio, "_global_mute", False)
    monkeypatch.setattr(audio, "get_sound_path", lambda _name: str(sound))
    monkeypatch.setattr(audio, "get_sound_duration", lambda _path: 1.0)
    monkeypatch.setattr(threading, "Thread", FakeThread)

    audio.play_sound("alert.wav", volume=5)

    assert started == [True]


def test_cleanup_screen_resets_singleton(monkeypatch):
    manager = screen_manager.ScreenManager(use_alternate_buffer=False)
    screen_manager._screen_manager = manager
    monkeypatch.setattr(manager, "exit_alternate_screen", lambda: None)

    screen_manager.cleanup_screen()

    assert screen_manager._screen_manager is None
