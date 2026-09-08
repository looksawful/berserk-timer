from pathlib import Path

import src.audio as audio


def test_stop_sound_never_uses_system_wide_killall(monkeypatch):
    monkeypatch.setattr(audio.sys, "platform", "linux")
    monkeypatch.setattr(audio, "_sound_process", None)

    audio.stop_sound()

    source = Path(audio.__file__).read_text(encoding="utf-8")
    assert "killall" not in source


def test_linux_audio_does_not_change_system_master_volume():
    source = Path(audio.__file__).read_text(encoding="utf-8")
    assert "amixer" not in source


def test_new_playback_stops_previous_playback_before_start(monkeypatch, tmp_path):
    sound = tmp_path / "alert.wav"
    sound.write_bytes(b"wave")
    calls = []

    monkeypatch.setattr(audio, "_global_mute", False)
    monkeypatch.setattr(audio, "_sound_playing", True)
    monkeypatch.setattr(audio, "get_sound_path", lambda _name: str(sound))
    monkeypatch.setattr(audio, "get_sound_duration", lambda _path: 1.0)
    monkeypatch.setattr(audio, "stop_sound", lambda: calls.append("stop"))

    class FakeThread:
        def __init__(self, target, daemon=False):
            self.target = target
            self.daemon = daemon

        def start(self):
            calls.append("start")

    monkeypatch.setattr(audio.threading, "Thread", FakeThread)

    audio.play_sound("alert.wav", 5)

    assert calls[:2] == ["stop", "start"]
