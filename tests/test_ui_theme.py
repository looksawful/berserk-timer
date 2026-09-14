from io import StringIO

from rich.console import Console

from src.ascii_art import ASCII_LOGO
from src.ui import PRIMARY, render_ascii_banner, render_startup_screen


def _terminal_console():
    stream = StringIO()
    console = Console(
        file=stream,
        force_terminal=True,
        color_system="truecolor",
        width=100,
    )
    return console, stream


def test_ascii_banner_keeps_art_and_emits_terminal_color() -> None:
    console, stream = _terminal_console()

    render_ascii_banner(console, ASCII_LOGO, "BERSERK TIMER", "0.3.0-beta")
    output = stream.getvalue()

    assert ASCII_LOGO.strip().splitlines()[0] in output
    assert "\x1b[" in output
    assert "BERSERK TIMER" in output
    assert "\u2500" in output


def test_startup_screen_restores_decorated_parameters_and_controls() -> None:
    console, stream = _terminal_console()

    render_startup_screen(
        console,
        version="0.3.0-beta",
        config_path=r"C:\Users\awful\AppData\Roaming\Berserk Timer\config.json",
        max_hours=24,
    )
    output = stream.getvalue()

    assert "PARAMETERS" in output
    assert "CONTROLS" in output
    assert "alert1.wav" in output
    assert "p" in output and "Pause / resume" in output
    assert "0.3.0-beta" in output
    assert "\x1b[" in output



def test_main_uses_decorated_startup_renderer() -> None:
    import inspect
    import src.main as main

    source = inspect.getsource(main.main)
    assert "render_startup_screen(" in source
    assert "print(ASCII_LOGO)" not in source


def test_cli_routes_ascii_screens_through_ui_renderer() -> None:
    import inspect
    import src.cli as cli

    source = inspect.getsource(cli)
    for artwork in (
        "ASCII_SETTINGS",
        "ASCII_BYE",
        "ASCII_WITNESS_LOG",
        "ASCII_FINISHED",
    ):
        assert f"print({artwork})" not in source
    assert "render_ascii_screen(" in source
    assert "render_help_screen(" in source


def test_primary_color_is_matrix_green() -> None:
    assert PRIMARY.lower() == "#00ff41"
