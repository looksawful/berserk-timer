import threading

import src.cli as cli


class FakeTimer:
    def __init__(self) -> None:
        self.paused = False
        self.stopped = False
        self.zeroed = False
        self.restarted = False
        self.silent = False

    def is_paused(self) -> bool:
        return self.paused

    def pause(self) -> None:
        self.paused = True

    def resume(self) -> None:
        self.paused = False

    def stop(self) -> None:
        self.stopped = True

    def zero(self) -> None:
        self.zeroed = True

    def restart(self) -> None:
        self.restarted = True

    def toggle_silent(self) -> None:
        self.silent = not self.silent

    def is_silent(self) -> bool:
        return self.silent


EXPECTED_KEYS = {"p", "q", "x", "r", "v", "d", "u", "g", "m", "s", "k", "h"}


def test_build_timer_command_handlers_exposes_exact_command_surface() -> None:
    timer = FakeTimer()
    handlers = cli.build_timer_command_handlers(
        timer,
        exit_flag=threading.Event(),
        suspend_display=threading.Event(),
        in_audio_menu=threading.Event(),
    )

    assert set(handlers) == EXPECTED_KEYS


def test_pause_handler_is_executable_without_keyboard_polling(monkeypatch) -> None:
    timer = FakeTimer()
    messages: list[str] = []
    monkeypatch.setattr(cli.console, "print", lambda message="": messages.append(str(message)))

    handlers = cli.build_timer_command_handlers(
        timer,
        exit_flag=threading.Event(),
        suspend_display=threading.Event(),
        in_audio_menu=threading.Event(),
    )

    handlers["p"]()

    assert timer.paused is True
    assert any("Timer paused" in message for message in messages)
