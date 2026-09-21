import shutil
import threading
import time
from typing import Callable, Dict, Optional, Tuple, TYPE_CHECKING

from rich.console import Console

from .ascii_art import ASCII_BYE, ASCII_SETTINGS, ASCII_FINISHED, ASCII_WITNESS_LOG
from .audio import (
    get_available_sounds,
    is_globally_muted,
    is_sound_playing,
    play_sound,
    stop_sound,
)
from .commands import dispatch_command
from .constants import MAX_TIMER_SECONDS
from .input_utils import read_input
from .keyboard_input import create_platform_keyboard_input
from .logger import delete_today_log, view_today_log
from .screen_manager import get_screen_manager
from .timer import TimerDurationError, validate_duration_seconds
from .ui import prompt_input, render_ascii_screen, render_help_screen, render_timer_status
from .version import __version__

if TYPE_CHECKING:
    from .timer import Timer

console = Console()
keyboard_input = create_platform_keyboard_input()

MAIN_LOOP_INTERVAL = 0.5
KEY_POLL_INTERVAL = 0.1
SOUND_PREVIEW_DURATION = 1.0
MIN_FULL_HINT_WIDTH = 80
VOLUME_LOW_THRESHOLD = 3
VOLUME_MID_THRESHOLD = 6
VOLUME_HIGH_THRESHOLD = 8
MAX_VOLUME = 10
MAX_DURATION_MINUTES = MAX_TIMER_SECONDS / 60


def validate_duration(seconds: float) -> Tuple[bool, str]:
    try:
        validate_duration_seconds(seconds)
    except TimerDurationError as exc:
        return False, str(exc)
    return True, ""


def safe_terminal_width(default: int = 80) -> int:
    try:
        width = shutil.get_terminal_size().columns
        if width and width > 0:
            return width
    except (OSError, ValueError):
        pass
    try:
        width = console.size.width
        if width and width > 0:
            return width
    except (OSError, ValueError, AttributeError):
        pass
    return default


def build_command_hint(width: int) -> str:
    full = "\\[p]ause \\[q]uit \\[x]zero timer \\[r]estart \\[v]iew \\[d]elete \\[u]pdate \\[g]oal \\[m]ute \\[s]ettings \\[h]elp"
    compact = "p q x r v d u g m s h"
    return full if width >= MIN_FULL_HINT_WIDTH else compact


def redraw_command_hints() -> None:
    screen = get_screen_manager()
    screen.clear_screen()
    width = safe_terminal_width()
    command_hint = build_command_hint(width)
    if width < MIN_FULL_HINT_WIDTH:
        console.print("[dim]Commands:[/dim]")
        console.print(f"[dim]{command_hint}[/dim]")
    else:
        console.print(f"[dim]Commands: {command_hint}[/dim]")
    console.print()


def show_volume_bar(volume: int, is_silent: bool = False) -> str:
    if is_silent or volume == 0:
        return "[blue][----------] SILENT[/blue]"

    filled = "#" * volume
    empty = "-" * (MAX_VOLUME - volume)

    if volume <= VOLUME_LOW_THRESHOLD:
        color = "blue"
    elif volume <= VOLUME_MID_THRESHOLD:
        color = "green"
    elif volume <= VOLUME_HIGH_THRESHOLD:
        color = "yellow"
    else:
        color = "red"

    return f"[{color}][{filled}{empty}] {volume}/{MAX_VOLUME}[/{color}]"


def build_timer_command_handlers(
    timer: "Timer",
    *,
    exit_flag: threading.Event,
    suspend_display: threading.Event,
    in_audio_menu: threading.Event,
) -> Dict[str, Callable[[], None]]:

    def toggle_pause_action() -> None:
        suspend_display.set()
        if timer.is_paused():
            timer.resume()
            console.print("\n[green]Timer resumed[/green]")
        else:
            timer.pause()
            console.print("\n[yellow]Timer paused[/yellow]")
        suspend_display.clear()

    def stop_action() -> None:
        suspend_display.set()
        try:
            confirmation_value = prompt_input(
                console,
                "\n[bold bright_red][!] Quit timer?[/bold bright_red] [grey62](y/n)[/grey62] "
            )
            confirmation = (
                confirmation_value.lower().strip()
                if confirmation_value is not None
                else ""
            )
            if confirmation in ("y", "yes"):
                timer.stop()
                exit_flag.set()
                render_ascii_screen(console, ASCII_BYE, "GOODBYE", border_style="bright_red")
                console.print("[red]Timer stopped by user.[/red]")
            else:
                console.print("[yellow]Quit cancelled. Timer continues.[/yellow]")
        finally:
            suspend_display.clear()

    def zero_action() -> None:
        suspend_display.set()
        timer.zero()
        console.print("\n[cyan]Timer zeroed[/cyan]")
        suspend_display.clear()

    def restart_action() -> None:
        suspend_display.set()
        timer.restart()
        console.print("\n[green]Timer restarted[/green]")
        suspend_display.clear()

    def view_log_action() -> None:
        suspend_display.set()
        try:
            screen = get_screen_manager()
            screen.clear_screen()
            render_ascii_screen(console, ASCII_WITNESS_LOG, "WITNESS LOG", border_style="bright_magenta")
            log_content = view_today_log()
            console.print(log_content)
            read_input("\nPress Enter to return to timer...")
            redraw_command_hints()
        finally:
            suspend_display.clear()

    def delete_logs_action() -> None:
        suspend_display.set()
        try:
            log_content = view_today_log()
            if log_content == "No log for today.":
                console.print("\n[yellow]No log for today to delete.[/yellow]")
                time.sleep(1.5)
            else:
                console.print("\n[yellow]Current log preview:[/yellow]")
                lines = log_content.split("\n")[:5]
                for line in lines:
                    console.print(f"  [dim]{line}[/dim]")
                if len(log_content.split("\n")) > 5:
                    console.print("  [dim]...[/dim]")

                confirmation_value = prompt_input(
                    console,
                    "\n[bold bright_red][!] Delete today's log?[/bold bright_red] [grey62](y/n)[/grey62] "
                )
                confirmation = (
                    confirmation_value.lower().strip()
                    if confirmation_value is not None
                    else ""
                )
                if confirmation in ("y", "yes"):
                    delete_today_log()
                    console.print("[red]Today's log deleted.[/red]")
                    time.sleep(1)
                else:
                    console.print("[green]Deletion cancelled.[/green]")
                    time.sleep(1)
        finally:
            suspend_display.clear()

    def update_duration_action() -> None:
        suspend_display.set()
        try:
            screen = get_screen_manager()
            screen.clear_screen()
            console.print(
                f"[dim]Current remaining: {timer.get_remaining_time_str()}[/dim]"
            )
            console.print(
                f"[dim]Max duration: {MAX_DURATION_MINUTES:.0f} minutes ({MAX_TIMER_SECONDS // 3600} hours)[/dim]\n"
            )

            duration_value = read_input("Enter new duration in minutes: ")
            if duration_value is None:
                console.print("[yellow]Cancelled.[/yellow]")
                time.sleep(1)
                redraw_command_hints()
                return
            user_input = duration_value.strip()
            if not user_input:
                console.print("[yellow]Cancelled.[/yellow]")
                time.sleep(1)
                redraw_command_hints()
                return

            new_duration_minutes = float(user_input)
            new_duration_seconds = new_duration_minutes * 60

            is_valid, error_msg = validate_duration(new_duration_seconds)
            if not is_valid:
                console.print(f"[red]Error: {error_msg}[/red]")
                time.sleep(2)
                redraw_command_hints()
                return

            timer.update_duration(new_duration_seconds)
            console.print(
                f"[green]Duration updated to {new_duration_minutes:.1f} minutes[/green]"
            )
            time.sleep(1)
            redraw_command_hints()
        except ValueError:
            console.print("[red]Invalid input. Please enter a number.[/red]")
            time.sleep(1.5)
            redraw_command_hints()
        finally:
            suspend_display.clear()

    def set_mute_action() -> None:
        suspend_display.set()
        timer.toggle_silent()
        if timer.is_silent():
            console.print("\n[blue]Silent mode: ON[/blue]")
        else:
            console.print("\n[green]Silent mode: OFF[/green]")
        suspend_display.clear()

    def set_goal_action() -> None:
        suspend_display.set()
        try:
            screen = get_screen_manager()
            screen.clear_screen()
            current_goal = timer.get_goal()
            if current_goal:
                console.print(f"[dim]Current goal: {current_goal}[/dim]\n")
            goal_value = read_input("Enter your goal (or press Enter to clear): ")
            if goal_value is None:
                console.print("[yellow]Cancelled.[/yellow]")
                time.sleep(1)
                redraw_command_hints()
                return
            new_goal = goal_value.strip()
            if new_goal:
                timer.set_goal(new_goal)
                console.print(f"[green]Goal set: {new_goal}[/green]")
            else:
                timer.set_goal(None)
                console.print("[yellow]Goal cleared.[/yellow]")
            time.sleep(1)
            redraw_command_hints()
        finally:
            suspend_display.clear()

    def show_help_action() -> None:
        suspend_display.set()
        try:
            screen = get_screen_manager()
            screen.clear_screen()
            render_help_screen(console, __version__)
            prompt_input(
                console,
                "\n[grey62]Press Enter to return to timer...[/grey62]",
            )
            redraw_command_hints()
        finally:
            suspend_display.clear()

    def change_sound_action() -> None:
        suspend_display.set()
        in_audio_menu.set()
        try:
            available_sounds = get_available_sounds()
            if not available_sounds:
                console.print("[red]No sound files found in assets directory![/red]")
                return

            current_sound = timer.get_sound_file()
            current_idx = (
                available_sounds.index(current_sound)
                if current_sound in available_sounds
                else 0
            )

            def show_menu_header() -> None:
                nonlocal current_idx
                is_silent = timer.is_silent()
                silent_label = " [SILENT]" if is_silent else ""
                screen = get_screen_manager()
                screen.clear_screen()
                render_ascii_screen(console, ASCII_SETTINGS, "AUDIO SETTINGS", border_style="bright_yellow")
                console.print("\n[bold cyan]═══ AUDIO SETTINGS ═══[/bold cyan]")
                console.print(
                    f"\n[yellow]Volume:[/yellow] {show_volume_bar(timer.get_volume(), is_silent)}{silent_label}"
                )
                console.print(
                    f"[yellow]Sound:[/yellow]  {timer.get_sound_file()} ({current_idx + 1}/{len(available_sounds)})"
                )
                if is_globally_muted():
                    console.print(
                        "[red]Global mute is ON; sounds are blocked until you disable mute.[/red]"
                    )
                console.print("\n[cyan]Available sounds:[/cyan]")
                for idx, sound in enumerate(available_sounds, 1):
                    marker = ">" if sound == timer.get_sound_file() else " "
                    console.print(f"  {marker} {idx}. {sound}")
                console.print("\n[bold]Commands:[/bold]")
                console.print("  [green]0[/green]       = Toggle silent mode")
                console.print("  [green]1-10[/green]    = Set volume (1=min, 10=max)")
                console.print("  [green]+/-[/green]     = Volume up/down")
                console.print("  [green]>[/green]       = Next sound")
                console.print("  [green]<[/green]       = Previous sound")
                console.print("  [green]t[/green]       = Test current settings")
                console.print("  [green]k[/green]       = Stop playing sound")
                console.print("  [green]Enter[/green]   = Close menu")

            while True:
                show_menu_header()
                choice_value = read_input("\n> ")
                if choice_value is None:
                    break
                choice = choice_value.strip()

                if not choice:
                    break

                if choice == "+":
                    current_vol = timer.get_volume()
                    if current_vol < MAX_VOLUME:
                        timer.set_volume(current_vol + 1)
                        if not timer.is_silent():
                            play_sound(timer.get_sound_file(), timer.get_volume())
                            time.sleep(SOUND_PREVIEW_DURATION)
                    continue

                if choice == "-":
                    current_vol = timer.get_volume()
                    if current_vol > 1:
                        timer.set_volume(current_vol - 1)
                        if not timer.is_silent():
                            play_sound(timer.get_sound_file(), timer.get_volume())
                            time.sleep(SOUND_PREVIEW_DURATION)
                    continue

                if choice.lower() == "k":
                    if is_sound_playing():
                        stop_sound()
                    continue

                if choice.isdigit():
                    num = int(choice)
                    if num == 0:
                        timer.toggle_silent()
                        if timer.is_silent():
                            stop_sound()
                    elif 1 <= num <= MAX_VOLUME:
                        timer.set_volume(num)
                        if not timer.is_silent():
                            play_sound(timer.get_sound_file(), num)
                            time.sleep(SOUND_PREVIEW_DURATION)
                    continue

                if choice == ">":
                    current_idx = (current_idx + 1) % len(available_sounds)
                    selected_sound = available_sounds[current_idx]
                    timer.set_sound_file(selected_sound)
                    if not timer.is_silent():
                        play_sound(selected_sound, timer.get_volume())
                        time.sleep(SOUND_PREVIEW_DURATION)
                    continue

                if choice == "<":
                    current_idx = (current_idx - 1) % len(available_sounds)
                    selected_sound = available_sounds[current_idx]
                    timer.set_sound_file(selected_sound)
                    if not timer.is_silent():
                        play_sound(selected_sound, timer.get_volume())
                        time.sleep(SOUND_PREVIEW_DURATION)
                    continue

                if choice.lower() == "t":
                    if not timer.is_silent():
                        play_sound(timer.get_sound_file(), timer.get_volume())
                        time.sleep(SOUND_PREVIEW_DURATION)
                    continue

                time.sleep(MAIN_LOOP_INTERVAL)
        finally:
            redraw_command_hints()
            suspend_display.clear()
            in_audio_menu.clear()

    def stop_sound_action() -> None:
        suspend_display.set()
        if is_sound_playing():
            stop_sound()
        suspend_display.clear()


    commands: Dict[str, Callable[[], None]] = {
        "p": toggle_pause_action,
        "q": stop_action,
        "x": zero_action,
        "r": restart_action,
        "v": view_log_action,
        "d": delete_logs_action,
        "u": update_duration_action,
        "g": set_goal_action,
        "m": set_mute_action,
        "s": change_sound_action,
        "k": stop_sound_action,
        "h": show_help_action,
    }


    return commands


def run_cli_timer(timer: "Timer") -> bool:
    exit_flag = threading.Event()
    suspend_display = threading.Event()
    in_audio_menu = threading.Event()
    stop_listener_event = threading.Event()

    commands = build_timer_command_handlers(
        timer,
        exit_flag=exit_flag,
        suspend_display=suspend_display,
        in_audio_menu=in_audio_menu,
    )

    def keyboard_listener() -> None:
        while (
            timer.is_running()
            and not exit_flag.is_set()
            and not stop_listener_event.is_set()
        ):
            if in_audio_menu.is_set():
                time.sleep(KEY_POLL_INTERVAL)
                continue
            key = keyboard_input.poll_key()
            if key is not None and dispatch_command(key, commands):
                if key.lower() == "q" and exit_flag.is_set():
                    break
            time.sleep(KEY_POLL_INTERVAL)

    listener = threading.Thread(target=keyboard_listener, daemon=True)
    listener.start()

    redraw_command_hints()

    last_remaining_str = ""

    while timer.is_running() and not exit_flag.is_set():
        if not suspend_display.is_set():
            remaining_str = timer.get_remaining_time_str()

            if remaining_str != last_remaining_str:
                screen = get_screen_manager()
                screen.clear_line()
                render_timer_status(
                    console,
                    remaining_str,
                    paused=timer.is_paused(),
                    silent=timer.is_silent(),
                    goal=timer.get_goal(),
                )
                last_remaining_str = remaining_str

        time.sleep(MAIN_LOOP_INTERVAL)

    print()

    stop_listener_event.set()
    if listener.is_alive():
        listener.join(timeout=1.0)
    return exit_flag.is_set()


def cli_witness_form(
    safe_word: str,
    timer: Optional["Timer"] = None,
    goal: Optional[str] = None,
    timer_end_time: Optional[float] = None,
    logging_mode: str = "witness",
    duration_minutes: float = 0,
    stop_repeating_alert: Optional[threading.Event] = None,
) -> Tuple[str, Optional[float]]:
    if logging_mode == "disabled":
        console.print("\n[dim]Logging disabled. Press Enter to continue...[/dim]")
        read_input()
        return ("Logging disabled.", timer_end_time)

    stop_alert_flag = threading.Event()

    def check_for_k_key() -> None:
        while not stop_alert_flag.is_set():
            key = keyboard_input.poll_key()
            if key is not None and key[0].lower() == "k":
                console.print("\n[yellow]Sound stopped (pressed 'k')[/yellow]")
                stop_sound()
                if stop_repeating_alert:
                    stop_repeating_alert.set()
                stop_alert_flag.set()
                return
            time.sleep(KEY_POLL_INTERVAL)

    k_listener = threading.Thread(target=check_for_k_key, daemon=True)
    k_listener.start()

    render_ascii_screen(console, ASCII_FINISHED, "FINISHED", border_style="bright_green")
    console.print("\n[bold cyan]⏰ TIMER FINISHED ⏰[/bold cyan]\n")
    if timer_end_time:
        import datetime

        completed_time = datetime.datetime.fromtimestamp(timer_end_time).strftime(
            "%H:%M:%S"
        )
        console.print(f"[yellow]Completed at:[/yellow] {completed_time}")
    if duration_minutes:
        console.print(f"[yellow]Duration:[/yellow]     {duration_minutes} minutes")
    if goal:
        console.print(f"[yellow]Goal:[/yellow]         {goal}")
    console.print()

    while True:
        if logging_mode == "confessor":
            prompt = "\n[bold red]You MUST describe what you did (cannot skip):[/bold red]\n> "
        elif logging_mode == "rage":
            prompt = "\nWhat did you accomplish? (or press Enter to skip, 'k' to stop alert): "
        else:
            prompt = "\nWhat did you accomplish? (or press Enter to skip"
            if safe_word:
                prompt += f", '{safe_word}' to cancel"
            prompt += ", 'k' to stop alert): "

        response_value = prompt_input(console, prompt)
        if response_value is None:
            stop_alert_flag.set()
            stop_sound()
            if stop_repeating_alert:
                stop_repeating_alert.set()
            return ("Witness skipped.", timer_end_time)

        response = response_value.strip()
        stop_alert_flag.set()
        stop_sound()
        if stop_repeating_alert:
            stop_repeating_alert.set()

        if safe_word and response.lower() == safe_word.lower():
            if stop_repeating_alert:
                stop_repeating_alert.set()
            return ("Witness skipped.", timer_end_time)
        if response.lower() == "k":
            stop_sound()
            if stop_repeating_alert:
                stop_repeating_alert.set()
            console.print("[yellow]Sound stopped.[/yellow]")
            continue
        if response:
            if stop_repeating_alert:
                stop_repeating_alert.set()
            return (response, timer_end_time)

        if logging_mode == "confessor":
            console.print(
                "[red]CONFESSOR mode: Input cannot be empty. You must describe your activity.[/red]"
            )
            continue
        elif logging_mode == "witness":
            confirmation_value = prompt_input(
                console,
                "\n[bright_yellow]Are you sure you want to skip witness? (y/n):[/bright_yellow] ",
            )
            if confirmation_value is None:
                if stop_repeating_alert:
                    stop_repeating_alert.set()
                return ("Witness skipped.", timer_end_time)
            confirmation = confirmation_value.strip().lower()
            if confirmation in ("y", "yes"):
                if stop_repeating_alert:
                    stop_repeating_alert.set()
                return ("Witness skipped.", timer_end_time)
            else:
                console.print("[cyan]Please provide your witness response:[/cyan]")
                continue
        else:
            if stop_repeating_alert:
                stop_repeating_alert.set()
            return ("Witness skipped.", timer_end_time)
