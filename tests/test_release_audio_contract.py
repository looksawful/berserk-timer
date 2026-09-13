from pathlib import Path

import src.audio as audio


EXPECTED_ALERTS = [f"alert{i}.wav" for i in range(1, 6)]


def test_all_shipped_alerts_are_discoverable_and_valid_wav_files() -> None:
    assert audio.get_available_sounds() == EXPECTED_ALERTS

    for name in EXPECTED_ALERTS:
        path = Path(audio.get_sound_path(name))
        assert path.is_file(), name
        assert audio.get_sound_duration(str(path)) > 0, name


def test_global_mute_blocks_new_playback(monkeypatch) -> None:
    started = []

    class FakeThread:
        def __init__(self, *args, **kwargs):
            started.append((args, kwargs))

        def start(self):
            started.append("started")

    monkeypatch.setattr(audio.threading, "Thread", FakeThread)
    audio.set_mute(True)
    try:
        audio.play_sound("alert1.wav", 5)
    finally:
        audio.set_mute(False)

    assert started == []
