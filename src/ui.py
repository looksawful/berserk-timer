from rich import box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from .ascii_art import ASCII_HELP, ASCII_LOGO, AUTHOR_SIGNATURE
from .input_utils import read_input

PRIMARY = "bright_red"
ACCENT = "bright_yellow"
SECONDARY = "bright_cyan"
SUCCESS = "bright_green"
MUTED = "grey62"


def render_ascii_banner(
    console: Console,
    artwork: str,
    title: str,
    subtitle: str | None = None,
    *,
    border_style: str = PRIMARY,
) -> None:
    body = Align.center(Text(artwork.strip("\n"), style=f"bold {border_style}"))
    console.print(
        Panel(
            body,
            box=box.ROUNDED,
            border_style=border_style,
            title=Text(f" {title} ", style=f"bold {border_style}"),
            subtitle=Text(f" {subtitle} ", style=MUTED) if subtitle else None,
            padding=(1, 2),
        )
    )


def _parameter_table(config_path: str, max_hours: int) -> Table:
    table = Table.grid(padding=(0, 2))
    table.add_column(style=MUTED, no_wrap=True)
    table.add_column(style="white")
    table.add_row("PRESETS", "xs 5m   s 10m   m 15m   l 20m   xl 25m   test 1m")
    table.add_row("LIMIT", f"{max_hours} hours")
    table.add_row("SOUNDS", "alert1.wav  alert2.wav  alert3.wav  alert4.wav  alert5.wav")
    table.add_row("VOLUME", "0-10, default 5")
    table.add_row("CONFIG", config_path)
    return table


def _controls_table() -> Table:
    table = Table.grid(padding=(0, 1))
    table.add_column(style=ACCENT, justify="right", no_wrap=True)
    table.add_column(style="white")
    table.add_column(style=ACCENT, justify="right", no_wrap=True)
    table.add_column(style="white")
    rows = (
        ("p", "Pause / resume", "q", "Quit"),
        ("x", "Zero timer", "r", "Restart"),
        ("v", "View log", "d", "Delete log"),
        ("u", "Update duration", "g", "Set goal"),
        ("m", "Mute", "s", "Audio settings"),
        ("k", "Stop sound", "h", "Help"),
    )
    for row in rows:
        table.add_row(*row)
    return table


def render_startup_screen(
    console: Console,
    *,
    version: str,
    config_path: str,
    max_hours: int,
) -> None:
    render_ascii_banner(console, ASCII_LOGO, "BERSERK TIMER", version)
    console.print(Align.center(Text(AUTHOR_SIGNATURE, style=MUTED)))
    console.print()
    console.print(
        Panel(
            _parameter_table(config_path, max_hours),
            title=Text(" PARAMETERS ", style=f"bold {ACCENT}"),
            border_style=ACCENT,
            box=box.ROUNDED,
            padding=(0, 1),
        )
    )
    console.print(
        Panel(
            _controls_table(),
            title=Text(" CONTROLS ", style=f"bold {SECONDARY}"),
            border_style=SECONDARY,
            box=box.ROUNDED,
            padding=(0, 1),
        )
    )
    console.print(Rule(style=MUTED))


def render_help_screen(console: Console, version: str) -> None:
    render_ascii_banner(console, ASCII_HELP, "HELP", version, border_style=SECONDARY)
    console.print(
        Panel(
            _controls_table(),
            title=Text(" TIMER COMMANDS ", style=f"bold {SECONDARY}"),
            border_style=SECONDARY,
            box=box.ROUNDED,
        )
    )


def render_ascii_screen(
    console: Console,
    artwork: str,
    title: str,
    *,
    border_style: str = PRIMARY,
) -> None:
    render_ascii_banner(
        console,
        artwork,
        title,
        border_style=border_style,
    )


def render_timer_status(
    console: Console,
    remaining: str,
    *,
    paused: bool = False,
    silent: bool = False,
    goal: str | None = None,
) -> None:
    status = Text()
    if paused:
        status.append("● PAUSED  ", style=f"bold {ACCENT}")
    else:
        status.append("● RUNNING  ", style=f"bold {SUCCESS}")
    if silent:
        status.append("MUTE  ", style=f"bold {SECONDARY}")
    status.append(remaining, style=f"bold {PRIMARY}")
    if goal:
        status.append("  ·  ", style=MUTED)
        status.append(goal, style="white")
    console.print(status, end="\r")


def prompt_input(console: Console, prompt: str) -> str | None:
    console.print(prompt, end="")
    return read_input()
