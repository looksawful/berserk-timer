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
