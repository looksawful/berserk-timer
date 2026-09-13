import math

import pytest

import src.logger as logger
from src.timer import Timer, TimerDurationError


def test_timer_rejects_nan_duration():
    with pytest.raises(TimerDurationError):
        Timer(math.nan)


@pytest.mark.parametrize(
    "name",
    [
        "get_available_sounds",
        "get_sound_duration",
        "get_sound_path",
        "is_globally_muted",
        "is_sound_playing",
        "play_sound",
        "set_mute",
        "stop_sound",
    ],
)
def test_logger_does_not_expose_audio_playback_api(name):
    assert not hasattr(logger, name)
