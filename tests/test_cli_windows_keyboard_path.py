import src.cli as cli


def test_windows_keyboard_listener_dispatches_quit_handler(monkeypatch) -> None:
    class FakeTimer:
        def __init__(self) -> None:
            self.running = True
            self.stopped = False

        def is_running(self) -> bool:
            return self.running

        def stop(self) -> None:
            self.stopped = True
            self.running = False

        def get_remaining_time_str(self) -> str:
            return "00:01"

        def is_paused(self) -> bool:
            return False

        def is_silent(self) -> bool:
            return False

        def get_goal(self) -> None:
            return None

    timer = FakeTimer()
    key_available = True

    def fake_kbhit() -> bool:
        return key_available

    def fake_getch() -> str:
        nonlocal key_available
        key_available = False
        return "q"

    monkeypatch.setattr(cli, "kbhit", fake_kbhit)
    monkeypatch.setattr(cli, "getch", fake_getch)
    monkeypatch.setattr(cli, "prompt_input", lambda *_args, **_kwargs: "y")
    monkeypatch.setattr(cli, "redraw_command_hints", lambda: None)
    monkeypatch.setattr(cli, "render_ascii_screen", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(cli.console, "print", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(cli, "MAIN_LOOP_INTERVAL", 0.001)
    monkeypatch.setattr(cli, "KEY_POLL_INTERVAL", 0.001)

    user_exited = cli.run_cli_timer(timer)

    assert timer.stopped is True
    assert user_exited is True
