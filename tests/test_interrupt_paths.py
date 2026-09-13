import argparse
import ast
import threading
import time
from pathlib import Path

import pytest

import src.cli as cli
import src.main as main
import src.session as session


def _direct_input_calls(module) -> list[int]:
    source = Path(module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    return [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "input"
    ]


@pytest.mark.parametrize("module", [main, session, cli])
def test_interactive_modules_do_not_call_builtin_input_directly(module) -> None:
    assert _direct_input_calls(module) == []


def test_main_initial_duration_eof_exits_without_starting_timer(monkeypatch) -> None:
    args = argparse.Namespace(
        duration=None,
        seconds=False,
        x=False,
        s=False,
        m=False,
        l=False,
        X=False,
        t=False,
        w=False,
        c=None,
        sound=None,
        mute=False,
        debug=True,
        show_help=False,
    )
    started = []

    monkeypatch.setattr(main, "parse_arguments", lambda: args)
    monkeypatch.setattr(main, "init_screen", lambda **_kwargs: None)
    monkeypatch.setattr(main, "cleanup_screen", lambda: None)
    monkeypatch.setattr(
        main,
        "load_config",
        lambda: {"presets": {}, "witness_mode": False},
    )
    monkeypatch.setattr(main, "run_timer_loop", lambda *_args, **_kwargs: started.append(True))

    def raise_eof(_prompt=""):
        raise EOFError

    monkeypatch.setattr("builtins.input", raise_eof)

    main.main()

    assert started == []


class _CompletedTimer:
    def __init__(self, duration, goal=None, sound_file="alert1.wav", volume=5):
        self.duration = duration
        self.goal = goal
        self.sound_file = sound_file
        self.volume = volume

    def set_volume(self, volume):
        self.volume = volume

    def start(self):
        pass

    def was_zeroed(self):
        return False

    def get_remaining_time(self):
        return 0


def _session_args() -> argparse.Namespace:
    return argparse.Namespace(seconds=False, sound=None, mute=False)


def _prepare_completed_session(monkeypatch) -> None:
    monkeypatch.setattr(session, "Timer", _CompletedTimer)
    monkeypatch.setattr(session, "run_cli_timer", lambda _timer: False)
    monkeypatch.setattr(session, "log_event", lambda _message: None)
    monkeypatch.setattr(session, "log_timer_start", lambda *_args: None)
    monkeypatch.setattr(
        session,
        "on_timer_end",
        lambda *_args, **_kwargs: (0.0, time.perf_counter()),
    )


def test_session_restart_prompt_eof_exits_cleanly(monkeypatch) -> None:
    _prepare_completed_session(monkeypatch)

    def raise_eof(_prompt=""):
        raise EOFError

    monkeypatch.setattr("builtins.input", raise_eof)

    session.run_timer_loop(
        _session_args(),
        {"sound_file": "alert1.wav", "volume": 5},
        60,
        False,
        None,
        None,
        False,
    )


def test_session_restart_duration_interrupt_exits_cleanly(monkeypatch) -> None:
    _prepare_completed_session(monkeypatch)
    answers = iter(["y"])

    def interrupted_input(_prompt=""):
        try:
            return next(answers)
        except StopIteration:
            raise KeyboardInterrupt from None

    monkeypatch.setattr("builtins.input", interrupted_input)

    session.run_timer_loop(
        _session_args(),
        {"sound_file": "alert1.wav", "volume": 5},
        60,
        False,
        None,
        None,
        False,
    )


def test_witness_skip_confirmation_interrupt_skips_and_stops_alert(monkeypatch) -> None:
    answers = iter([""])

    def interrupted_input(_prompt=""):
        try:
            return next(answers)
        except StopIteration:
            raise EOFError from None

    stop_repeating_alert = threading.Event()
    monkeypatch.setattr("builtins.input", interrupted_input)
    monkeypatch.setattr(cli, "kbhit", lambda: False)
    monkeypatch.setattr(cli, "stop_sound", lambda: None)

    response, timer_end_time = cli.cli_witness_form(
        "skip",
        timer_end_time=123.0,
        stop_repeating_alert=stop_repeating_alert,
    )

    assert response == "Witness skipped."
    assert timer_end_time == 123.0
    assert stop_repeating_alert.is_set()
