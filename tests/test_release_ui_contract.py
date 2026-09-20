import inspect

import src.ascii_art as ascii_art
import src.cli as cli
import src.main as main


ASCII_NAMES = (
    "ASCII_LOGO",
    "ASCII_SETTINGS",
    "ASCII_HELP",
    "ASCII_BYE",
    "ASCII_WITNESS_LOG",
    "ASCII_FINISHED",
)
EXPECTED_COMMAND_KEYS = {"p", "q", "x", "r", "v", "d", "u", "g", "m", "s", "k", "h"}


def test_release_ascii_art_is_present_and_multiline() -> None:
    for name in ASCII_NAMES:
        artwork = getattr(ascii_art, name)
        assert artwork.strip()
        assert "\n" in artwork


def test_help_still_renders_ascii_through_ui_layer() -> None:
    source = inspect.getsource(main.show_help)
    assert "render_help_screen(console, __version__)" in source


def test_timer_command_surface_and_dispatch_are_preserved() -> None:
    builder_source = inspect.getsource(cli.build_timer_command_handlers)
    run_source = inspect.getsource(cli.run_cli_timer)

    for key in EXPECTED_COMMAND_KEYS:
        assert f'"{key}":' in builder_source

    assert "commands = build_timer_command_handlers(" in run_source
    assert "dispatch_command(key, commands)" in run_source
