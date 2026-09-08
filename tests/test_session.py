import argparse

import src.session as session


class FakeTimer:
    def __init__(self, duration, goal=None, sound_file="alert1.wav", volume=5):
        self.duration = duration
        self.goal = goal
        self.sound_file = sound_file
        self.volume = volume
        self.started = False
        self.zeroed = False
        self.remaining = 0

    def set_volume(self, volume):
        self.volume = volume

    def start(self):
        self.started = True

    def was_zeroed(self):
        return self.zeroed

    def get_remaining_time(self):
        return self.remaining


def test_run_timer_loop_composes_timer_and_cli_without_terminal_internals(monkeypatch):
    created = []

    def make_timer(*args, **kwargs):
        timer = FakeTimer(*args, **kwargs)
        created.append(timer)
        return timer

    monkeypatch.setattr(session, "Timer", make_timer)
    monkeypatch.setattr(session, "run_cli_timer", lambda timer: True)
    monkeypatch.setattr(session, "log_event", lambda _message: None)
    monkeypatch.setattr(session, "log_timer_start", lambda *_args: None)

    args = argparse.Namespace(seconds=False, sound=None, mute=True)

    try:
        session.run_timer_loop(
            args,
            {"sound_file": "alert2.wav", "volume": 7},
            60,
            False,
            None,
            "focus",
            False,
        )
    except SystemExit as exc:
        assert exc.code == 0

    assert len(created) == 1
    assert created[0].started is True
    assert created[0].sound_file == "alert2.wav"
    assert created[0].volume == 0
