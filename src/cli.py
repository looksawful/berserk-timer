import select
import shutil
import sys
import threading
import time
from typing import Callable, Dict, Optional, Tuple, TYPE_CHECKING

from rich.console import Console

from .ascii_art import ASCII_BYE, ASCII_HELP, ASCII_SETTINGS, ASCII_FINISHED, ASCII_WITNESS_LOG
from .audio import (
    get_available_sounds,
    is_globally_muted,
    is_sound_playing,
    play_sound,
    stop_sound,
)
from .commands import dispatch_command
from .constants import MAX_TIMER_SECONDS
from .logger import delete_today_log, view_today_log
from .screen_manager import get_screen_manager
from .timer import TimerDurationError, validate_duration_seconds

if TYPE_CHECKING:
    from .timer import Timer

console = Console()

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


if sys.platform.startswith("win"):
    import msvcrt

    def kbhit() -> bool:
        return msvcrt.kbhit()

    def getch() -> str:
        try:
            return msvcrt.getch().decode("utf-8", errors="ignore")
        except (UnicodeDecodeError, OSError):
            return ""

else:
    import termios
    import tty

    def kbhit() -> bool:
        dr, _, _ = select.select([sys.stdin], [], [], 0)
        return bool(dr)

    def getch() -> str:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


def run_cli_timer(timer: "Timer") -> bool:
    exit_flag = threading.Event()
    suspend_display = threading.Event()
    in_audio_menu = threading.Event()
    stop_listener_event = threading.Event()

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
            confirmation = (
                input("\n[!] Are you sure you want to quit the timer? (y/n): ")
                .lower()
                .strip()
            )
            if confirmation in ("y", "yes"):
                timer.stop()
                exit_flag.set()
                print(ASCII_BYE)
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
            print(ASCII_WITNESS_LOG)
            log_content = view_today_log()
            console.print(log_content)
            input("\nPress Enter to return to timer...")
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

                confirmation = (
                    input("\n[!] Are you sure you want to delete today's log? (y/n): ")
                    .lower()
                    .strip()
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

            user_input = input("Enter new duration in minutes: ").strip()
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
            new_goal = input("Enter your goal (or press Enter to clear): ").strip()
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
            print(ASCII_HELP)
            console.print("\n[bold cyan]TIMER COMMANDS:[/bold cyan]")
            console.print("  [green]p[/green] - Pause/Resume timer")
            console.print("  [green]q[/green] - Quit timer (with confirmation)")
            console.print("  [green]x[/green] - Zero the timer")
            console.print("  [green]r[/green] - Restart timer from beginning")
            console.print("  [green]v[/green] - View today's witness log")
            console.print("  [green]d[/green] - Delete today's witness log")
            console.print("  [green]u[/green] - Update duration (change timer length)")
            console.print("  [green]g[/green] - Set/change goal for this session")
            console.print("  [green]m[/green] - Toggle silent mode on/off")
            console.print(
                "  [green]s[/green] - Open audio settings (sound file and volume)"
            )
            console.print("  [green]h[/green] - Show this help screen")
            console.print("  [green]k[/green] - Stop currently playing sound")
            input("\nPress Enter to return to timer...")
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
                print(ASCII_SETTINGS)
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
                try:
                    choice = input("\n> ").strip()
                except (EOFError, KeyboardInterrupt):
                    break

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

    def keyboard_listener() -> None:
        while (
            timer.is_running()
            and not exit_flag.is_set()
            and not stop_listener_event.is_set()
        ):
            if in_audio_menu.is_set():
                time.sleep(KEY_POLL_INTERVAL)
                continue
            if kbhit():
                try:
                    key = getch()
                except (UnicodeDecodeError, OSError):
                    continue

                if not key:
                    continue

                if ord(key[0]) == 27:
                    while kbhit():
                        try:
                            getch()
                        except (UnicodeDecodeError, OSError):
                            break
                    continue

                if ord(key[0]) == 224:
                    if kbhit():
                        try:
                            getch()
                        except (UnicodeDecodeError, OSError):
                            pass
                    continue

                if ord(key[0]) < 32:
                    continue

                if dispatch_command(key, commands):
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
                silent_marker = "[SILENT] " if timer.is_silent() else ""
                paused_marker = "[PAUSED] " if timer.is_paused() else ""
                status = f"{silent_marker}{paused_marker}Time: {remaining_str}"

                width = safe_terminal_width()
                sys.stdout.write(f"\r{' ' * width}\r{status}")
                sys.stdout.flush()

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
        input()
        return ("Logging disabled.", timer_end_time)

    stop_alert_flag = threading.Event()

    def check_for_k_key() -> None:
        while not stop_alert_flag.is_set():
            if kbhit():
                try:
                    key = getch()
                    if key and key[0].lower() == "k":
                        console.print("\n[yellow]Sound stopped (pressed 'k')[/yellow]")
                        stop_sound()
                        if stop_repeating_alert:
                            stop_repeating_alert.set()
                        stop_alert_flag.set()
                        return
                except (UnicodeDecodeError, OSError):
                    pass
            time.sleep(KEY_POLL_INTERVAL)

    k_listener = threading.Thread(target=check_for_k_key, daemon=True)
    k_listener.start()

    print(ASCII_FINISHED)
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

        try:
            response = input(prompt).strip()
            stop_alert_flag.set()
            stop_sound()
            if stop_repeating_alert:
                stop_repeating_alert.set()
        except (EOFError, KeyboardInterrupt):
            stop_alert_flag.set()
            stop_sound()
            if stop_repeating_alert:
                stop_repeating_alert.set()
            return ("Witness skipped.", timer_end_time)

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
            confirmation = (
                input(
                    "\n[yellow]Are you sure you want to skip witness? (y/n):[/yellow] "
                )
                .strip()
                .lower()
            )
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
