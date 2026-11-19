"""Regression for CLI --mute and interactive sound controls (Issue #43)."""

import sys
import threading
import time

import pytest

import src.audio as audio
import src.cli as cli
import src.main as main
import src.session as session


@pytest.mark.parametrize(
    ("action", "menu_inputs", "expected_volume"),
    [
        ("m", (), 5),
        ("s", ("3", ""), 3),
    ],
)
def test_start_muted_then_unmute_allows_alerts(
    monkeypatch, action, menu_inputs, expected_volume
):
    """A muted launch must not leave an invisible playback block after unmute."""
    config = {
        "presets": {},
        "volume": 5,
        "sound_file": "alert1.wav",
        "witness_mode": False,
        "messages": [],
    }
    observed = []
    previews = []
    inputs = iter(menu_inputs)

    monkeypatch.setattr(sys, "argv", ["berserk", "1", "--mute"])
    monkeypatch.setattr(main, "configure_stdout_encoding", lambda: None)
    monkeypatch.setattr(main, "render_startup_screen", lambda *a, **k: None)
    monkeypatch.setattr(main, "load_config", lambda: config)
    monkeypatch.setattr(main, "prompt_input", lambda *a, **k: "")
    monkeypatch.setattr(main, "init_screen", lambda **k: None)
    monkeypatch.setattr(main.atexit, "register", lambda func: None)
    monkeypatch.setattr(main, "log_event", lambda message: None)
    monkeypatch.setattr(session, "log_event", lambda message: None)
    monkeypatch.setattr(session, "log_timer_start", lambda *a, **k: None)
    monkeypatch.setattr(
        session, "on_timer_end", lambda *a, **k: (time.time(), time.perf_counter())
    )
    monkeypatch.setattr(session, "read_input", lambda prompt: "n")
    monkeypatch.setattr(cli, "redraw_command_hints", lambda: None)
    monkeypatch.setattr(cli, "get_available_sounds", lambda: ["alert1.wav"])
    monkeypatch.setattr(cli, "read_input", lambda prompt: next(inputs))
    monkeypatch.setattr(
        cli,
        "get_screen_manager",
        lambda: type("Screen", (), {"clear_screen": lambda self: None})(),
    )
    monkeypatch.setattr(cli, "render_ascii_screen", lambda *a, **k: None)
    monkeypatch.setattr(
        cli, "play_sound", lambda *args, **kwargs: previews.append(args)
    )

    def exercise_controls(timer):
        try:
            assert timer.is_silent()
            assert timer.get_volume() == 0

            handlers = cli.build_timer_command_handlers(
                timer,
                exit_flag=threading.Event(),
                suspend_display=threading.Event(),
                in_audio_menu=threading.Event(),
            )
            handlers[action]()
            observed.append(
                (timer.is_silent(), timer.get_volume(), audio.is_globally_muted())
            )
        finally:
            timer.zero()
        return False

    monkeypatch.setattr(session, "run_cli_timer", exercise_controls)
    try:
        main.main()
        assert observed == [(False, expected_volume, False)]
        if action == "s":
            assert previews == [("alert1.wav", 3)]
    finally:
        audio.set_mute(False)


def test_muted_launch_cancelled_audio_menu_remains_silent(monkeypatch):
    """An empty settings menu must not accidentally enable the sound."""
    from src.timer import Timer

    timer = Timer(60, volume=5)
    timer.set_volume(0)
    monkeypatch.setattr(cli, "get_available_sounds", lambda: ["alert1.wav"])
    monkeypatch.setattr(
        cli,
        "get_screen_manager",
        lambda: type("Screen", (), {"clear_screen": lambda self: None})(),
    )
    monkeypatch.setattr(cli, "render_ascii_screen", lambda *a, **k: None)
    monkeypatch.setattr(cli, "redraw_command_hints", lambda: None)
    monkeypatch.setattr(cli, "read_input", lambda prompt: "")
    previews = []
    monkeypatch.setattr(cli, "play_sound", lambda *a, **k: previews.append((a, k)))

    handlers = cli.build_timer_command_handlers(
        timer,
        exit_flag=threading.Event(),
        suspend_display=threading.Event(),
        in_audio_menu=threading.Event(),
    )
    handlers["s"]()
    assert timer.is_silent()
    assert timer.get_volume() == 0
    assert previews == []
