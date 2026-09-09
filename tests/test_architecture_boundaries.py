import src.audio as audio
import src.cli as cli
import src.logger as logger


def test_cli_uses_audio_module_functions_directly():
    assert cli.get_available_sounds is audio.get_available_sounds
    assert cli.is_globally_muted is audio.is_globally_muted
    assert cli.is_sound_playing is audio.is_sound_playing
    assert cli.play_sound is audio.play_sound
    assert cli.stop_sound is audio.stop_sound


def test_logger_does_not_expose_audio_compatibility_api():
    for name in (
        "get_available_sounds",
        "get_sound_duration",
        "get_sound_path",
        "is_globally_muted",
        "is_sound_playing",
        "play_sound",
        "set_mute",
        "stop_sound",
    ):
        assert not hasattr(logger, name)


def test_cli_does_not_own_duration_validation_rules():
    assert not hasattr(cli, "validate_duration")
