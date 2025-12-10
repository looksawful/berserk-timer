"""Module cli.py: CLI interface for the Berserk Timer application."""
import logging
import os
import sys
import time
import threading
import select
import shutil
from typing import Callable, Dict, Optional
from rich.console import Console
from rich.text import Text
from .logger import view_today_log, delete_today_log, get_available_sounds, play_sound, stop_sound, is_sound_playing
from .ascii_art import ASCII_SETTINGS, ASCII_HELP, ASCII_BYE

console = Console()


def safe_terminal_width(default: int = 80) -> int:
    """Return current terminal width with fallbacks for Windows shells that glitch during resize."""
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
    except Exception:
        pass
    return default


def clear_console() -> None:
    """Cross-platform console clear (handles Windows Terminal / PowerShell / Git Bash)."""
    try:
        console.clear()
    except Exception:
        cmd = "cls" if os.name == "nt" else "clear"
        os.system(cmd)


def clear_status_line(width: int) -> None:
    """Fully wipe the current status line before rewriting it."""
    sys.stdout.write("\r" + (" " * max(width, 0)) + "\r")
    sys.stdout.flush()


def build_command_hint(width: int) -> str:
    """Build command hint string based on terminal width."""
    full = "[p]ause [q]uit [x]zero [r]estart [v]iew [d]elete [u]pdate [g]oal [m]ute [s]ound [h]elp"
    compact = "[p][q][x][r][v][d][u][g][m][s][h]"
    return full if width >= 80 else compact


if sys.platform.startswith("win"):
    import msvcrt

    def kbhit() -> bool:
        return msvcrt.kbhit()

    def getch() -> str:
        return msvcrt.getch().decode("utf-8")
else:
    import tty
    import termios

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


def run_cli_timer(timer) -> bool:
    """Runs the command-line timer interface.
    Args:
        timer: Timer instance.
    Returns:
        bool: True if the user exited the timer, False otherwise.
    """
    exit_flag = False
    suspend_display = threading.Event()
    in_audio_menu = False  # Suppress global hotkeys while inside audio settings

    def toggle_pause_action() -> None:
        suspend_display.set()
        if timer.is_paused():
            timer.resume()
            console.print("[green]Timer resumed.[/green]")
        else:
            timer.pause()
            console.print("[yellow]Timer paused. Press 'p' again to resume.[/yellow]")
        width = safe_terminal_width()
        print(f"Commands: {build_command_hint(width)}")
        print()
        suspend_display.clear()

    def stop_action() -> None:
        nonlocal exit_flag
        suspend_display.set()
        try:
            confirmation = input("\n[!] Are you sure you want to quit the timer? (y/n): ").lower().strip()
            if confirmation in ('y', 'yes', 'д', 'да'):
                timer.stop()
                exit_flag = True
                print(ASCII_BYE)
                console.print("[red]Timer stopped by user.[/red]")
            else:
                console.print("[yellow]Quit cancelled. Timer continues.[/yellow]")
        finally:
            suspend_display.clear()

    def zero_action() -> None:
        suspend_display.set()
        timer.zero()
        console.print("[blue]Timer zeroed.[/blue]")
        print(f"Commands: {build_command_hint(safe_terminal_width())}")
        print()
        suspend_display.clear()

    def restart_action() -> None:
        suspend_display.set()
        timer.restart()
        console.print("[cyan]Timer restarted.[/cyan]")
        print(f"Commands: {build_command_hint(safe_terminal_width())}")
        print()
        suspend_display.clear()

    def view_log_action() -> None:
        suspend_display.set()
        log_content = view_today_log()
        console.print("[magenta]Today's Witness Log:[/magenta]")
        console.print(log_content)
        print(f"Commands: {build_command_hint(safe_terminal_width())}")
        print()
        suspend_display.clear()

    def delete_logs_action() -> None:
        suspend_display.set()
        delete_today_log()
        console.print("[bold red]Today's log deleted.[/bold red]")
        print(f"Commands: {build_command_hint(safe_terminal_width())}")
        print()
        suspend_display.clear()

    def update_duration_action() -> None:
        suspend_display.set()
        try:
            user_input = input("\nEnter new duration in minutes: ")
            new_duration = float(user_input) * 60
            timer.update_duration(new_duration)
            console.print(
                f"[green]Timer duration updated to {new_duration / 60} minutes.[/green]")
        except ValueError:
            console.print("[red]Invalid input for duration update.[/red]")
        finally:
            suspend_display.clear()

    def set_mute_action():
        suspend_display.set()
        timer.toggle_silent()  # Toggle silent mode in timer
        status = "enabled" if timer.is_silent() else "disabled"
        volume_info = f" Volume set to {timer.get_volume()}." if not timer.is_silent() else ""
        console.print(f"[yellow]Silent mode {status}.{volume_info}[/yellow]")
        print(f"Commands: {build_command_hint(safe_terminal_width())}")
        print()
        suspend_display.clear()

    def set_goal_action() -> None:
        suspend_display.set()
        try:
            new_goal = input("\nEnter your goal: ")
            timer.set_goal(new_goal)
            console.print(f"[blue]Goal set to: {new_goal}[/blue]")
        finally:
            suspend_display.clear()

    def show_help_action() -> None:
        """Show help screen with ASCII header during timer."""
        suspend_display.set()
        try:
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
            console.print("  [green]s[/green] - Open audio settings (sound file and volume)")
            console.print("  [green]h[/green] - Show this help screen")
            console.print("  [green]k[/green] - Stop currently playing sound")
            input("\nPress Enter to return to timer...")
        finally:
            suspend_display.clear()

    def show_volume_bar(volume: int, is_silent: bool = False) -> str:
        """Generate ASCII volume bar with color gradient.
        0 = blue (silent), 1-3 = blue, 4-6 = green, 7-8 = yellow, 9-10 = red
        """
        if is_silent or volume == 0:
            return "[blue][----------] SILENT[/blue]"

        filled = "#" * volume
        empty = "-" * (10 - volume)

        # Color gradient based on volume
        if volume <= 3:
            color = "blue"
        elif volume <= 6:
            color = "green"
        elif volume <= 8:
            color = "yellow"
        else:
            color = "red"

        return f"[{color}][{filled}{empty}] {volume}/10[/{color}]"

    def change_sound_action() -> None:
        suspend_display.set()
        nonlocal in_audio_menu
        in_audio_menu = True
        try:
            available_sounds = get_available_sounds()
            if not available_sounds:
                console.print("[red]No sound files found in assets directory![/red]")
                return

            current_volume = timer.get_volume()
            current_sound = timer.get_sound_file()
            is_silent = timer.is_silent()

            # Find current sound index
            current_idx = available_sounds.index(current_sound) if current_sound in available_sounds else 0

            print(ASCII_SETTINGS)
            console.print("\n[bold cyan]═══ AUDIO SETTINGS ═══[/bold cyan]")
            console.print("
[bold cyan]=== AUDIO SETTINGS ===[/bold cyan]")
            console.print(f"\n[yellow]Volume:[/yellow] {show_volume_bar(current_volume, is_silent)}{silent_label}")
            console.print(f"[yellow]Sound:[/yellow]  {current_sound} ({current_idx + 1}/{len(available_sounds)})")

            console.print("\n[cyan]Available sounds:[/cyan]")
            for idx, sound in enumerate(available_sounds, 1):
                marker = ">" if sound == current_sound else " "
                console.print(f"  {marker} {idx}. {sound}")

            console.print("\n[bold]Commands:[/bold]")
            console.print("  [green]0[/green]       = Toggle silent mode")
            console.print("  [green]1-10[/green]    = Set volume (1=min, 10=max)")
            console.print("  [green]>[/green]       = Next sound")
            console.print("  [green]<[/green]       = Previous sound")
            console.print("  [green]t[/green]       = Test current settings")
            console.print("  [green]k[/green]       = Stop playing sound")
            console.print("  [green]Enter[/green]   = Close menu")

            import select
            import sys

            def show_menu_header():
                """Reprint menu header to keep it in place."""
                console.clear()
                print(ASCII_SETTINGS)
                console.print("\n[bold cyan]═══ AUDIO SETTINGS ═══[/bold cyan]")
                console.print("
[bold cyan]=== AUDIO SETTINGS ===[/bold cyan]")
                console.print(f"\n[yellow]Volume:[/yellow] {show_volume_bar(timer.get_volume(), is_silent)}{silent_label}")
                console.print(f"[yellow]Sound:[/yellow]  {timer.get_sound_file()} ({current_idx + 1}/{len(available_sounds)})")
                console.print("\n[cyan]Available sounds:[/cyan]")
                for idx, sound in enumerate(available_sounds, 1):
                    marker = ">" if sound == timer.get_sound_file() else " "
                    console.print(f"  {marker} {idx}. {sound}")
                console.print("\n[bold]Commands:[/bold]")
                console.print("  [green]0[/green]       = Toggle silent mode")
                console.print("  [green]1-10[/green]    = Set volume (1=min, 10=max)")
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
                    console.print("[yellow]Settings saved.[/yellow]")
                    time.sleep(0.5)
                    break

                if choice.lower() == 'k':
                    if is_sound_playing():
                        stop_sound()
                        console.print("[yellow]Sound stopped.[/yellow]")
                    else:
                        console.print("[yellow]No sound is playing.[/yellow]")
                    time.sleep(0.8)
                    continue

                if choice.isdigit():
                    num = int(choice)
                    if num == 0:
                        timer.toggle_silent()
                        is_silent = timer.is_silent()
                        if is_silent:
                            stop_sound()
                        status = "enabled" if is_silent else "disabled"
                        console.print(f"[yellow]Silent mode {status}.[/yellow]")
                        time.sleep(0.8)
                    elif 1 <= num <= 10:
                        timer.set_volume(num)
                        console.print(f"[green]Volume set to {num}/10[/green]")
                        play_sound(timer.get_sound_file(), num)
                        time.sleep(1.0)
                    else:
                        console.print("[red]Volume must be between 0 and 10![/red]")
                        time.sleep(0.8)
                    continue

                if choice == '>':
                    current_idx = (current_idx + 1) % len(available_sounds)
                    selected_sound = available_sounds[current_idx]
                    timer.set_sound_file(selected_sound)
                    console.print(f"[green]Sound changed to: {selected_sound}[/green]")
                    play_sound(selected_sound, timer.get_volume())
                    time.sleep(1.0)
                    continue

                if choice == '<':
                    current_idx = (current_idx - 1) % len(available_sounds)
                    selected_sound = available_sounds[current_idx]
                    timer.set_sound_file(selected_sound)
                    console.print(f"[green]Sound changed to: {selected_sound}[/green]")
                    play_sound(selected_sound, timer.get_volume())
                    time.sleep(1.0)
                    continue

                if choice.lower() == 't':
                    if timer.is_silent():
                        console.print("[yellow]Silent mode is ON - test will not play sound[/yellow]")
                        time.sleep(0.8)
                    else:
                        console.print(f"[cyan]Testing: {timer.get_sound_file()} at volume {timer.get_volume()}/10...[/cyan]")
                        play_sound(timer.get_sound_file(), timer.get_volume())
                        time.sleep(1.0)
                    continue

                console.print("[red]Invalid command! Use: 0 (silent), 1-10 (volume), </> (sound), t (test), k (stop), or Enter[/red]")
                time.sleep(0.8)
        finally:
            suspend_display.clear()
            in_audio_menu = False

    def stop_sound_action() -> None:
        suspend_display.set()
        width = safe_terminal_width()
        print("\r" + " " * width + "\r", end='', flush=True)
        if is_sound_playing():
            stop_sound()
            console.print("[yellow]Sound stopped.[/yellow]")
        else:
            console.print("[yellow]No sound is playing.[/yellow]")
        # Reprint hints after message
        print(f"Commands: {build_command_hint(width)}")
        print()
        suspend_display.clear()

    commands: Dict[str, Callable[[], None]] = {
        'p': toggle_pause_action,
        'q': stop_action,
        'x': zero_action,
        'r': restart_action,
        'v': view_log_action,
        'd': delete_logs_action,
        'u': update_duration_action,
        'g': set_goal_action,
        'm': set_mute_action,
        's': change_sound_action,
        'k': stop_sound_action,
        'h': show_help_action
    }

    def keyboard_listener() -> None:
        nonlocal exit_flag
        while timer.is_running() and not exit_flag:
            if in_audio_menu:
                # Do not process global hotkeys while audio menu is active
                time.sleep(0.05)
                continue
            if kbhit():
                try:
                    key = getch().lower()
                except (UnicodeDecodeError, OSError):
                    continue

                # Ignore control characters, escape sequences, and special keys
                if ord(key) < 32 or ord(key) == 27:  # Control chars and ESC
                    # Flush any remaining buffered input from paste/click
                    while kbhit():
                        try:
                            getch()
                        except:
                            break
                    continue

                if key in commands:
                    commands[key]()
                    # Only break if exit_flag was actually set (user confirmed quit)
                    if key == 'x' or (key == 'q' and exit_flag):
                        break
                else:
                    # For unknown printable keys, flush input buffer to prevent paste spam
                    while kbhit():
                        try:
                            getch()
                        except:
                            break
            time.sleep(0.1)

    listener = threading.Thread(target=keyboard_listener, daemon=True)
    listener.start()

    last_width = safe_terminal_width()
    last_render_time = 0.0
    last_remaining_str = ""
    last_status_width = last_width

    while timer.is_running() and not exit_flag:
        if not suspend_display.is_set():
            width = safe_terminal_width()

            # Detect terminal resize and clear screen to remove old wrapped lines
            if width != last_width:
                clear_console()

                # Reprint static hint line
                print(f"Commands: {build_command_hint(width)}")
                print()  # spacer line for status
                last_width = width
                # Force next render
                last_remaining_str = ""
                last_render_time = 0.0
                last_status_width = width
                # Skip this iteration to let screen settle
                time.sleep(0.1)
                continue

            # Throttle updates to ~1Hz and only when time changes
            now = time.time()
            remaining_str = timer.get_remaining_time_str()
            if now - last_render_time < 0.9 and remaining_str == last_remaining_str:
                time.sleep(0.1)
                continue
            last_render_time = now
            last_remaining_str = remaining_str

            silent_marker = "[SILENT] " if timer.is_silent() else ""
            hints = build_command_hint(width)

            # Build status line
            msg = f"{silent_marker}Time: {remaining_str} | {hints}"

            # Truncate to width minus margin to prevent wrap
            safe_width = max(10, width - 1)
            if len(msg) >= safe_width:
                msg = msg[:safe_width - 3] + "..."

            clear_status_line(max(last_status_width, safe_width))
            sys.stdout.write("\r" + msg.ljust(safe_width))
            sys.stdout.flush()
            last_status_width = safe_width
        time.sleep(0.1)
    console.print()
    return exit_flag


def enter_paused_mode(timer) -> None:
    """Enter paused timer mode to access settings and logs."""
    console.print("\n[cyan]═══ PAUSED MODE ═══[/cyan]")
    console.print("
[cyan]=== PAUSED MODE ===[/cyan]")
    console.print("[yellow]Press 'p' to resume, 'q' to exit menu, or use other commands.[/yellow]\n")

    # Ensure timer is running before pausing
    if not timer.is_running():
        timer.start()
    timer.pause()

    run_cli_timer(timer)
    console.print("\n[cyan]Returning to dialog...[/cyan]\n")


def cli_witness_form(safe_word: str, timer=None, goal: Optional[str] = None, timer_end_time: float = None) -> tuple:
    """Witness form with optional paused mode access.
    Args:
        safe_word: Word to skip witness logging
        timer: Optional timer instance to enter paused mode
        goal: Optional goal set at timer start; if None, empty input is allowed
        timer_end_time: Timestamp when timer ended (time.time())
    Returns:
        tuple: (response, timer_end_time)
    """
    import time
    import threading

    # Create a flag to stop the repeating alert from within the input thread
    stop_alert_flag = threading.Event()

    def check_for_k_key():
        """Background thread to check for 'k' key press to stop alert."""
        while not stop_alert_flag.is_set():
            if kbhit():
                try:
                    key = getch().lower()
                    if key == 'k':
                        console.print("\n[yellow]Sound stopped (pressed 'k')[/yellow]")
                        stop_sound()
                        stop_alert_flag.set()
                        return
                except (UnicodeDecodeError, Exception):
                    pass
            time.sleep(0.05)

    # Start background thread to listen for 'k' key
    k_listener = threading.Thread(target=check_for_k_key, daemon=True)
    k_listener.start()

    while True:
        # Show static prompt without elapsed time
        prompt = f"\nTimer finished. Please enter what you were doing, press Enter to skip"
        if safe_word:
            prompt += f", or type '{safe_word}' to cancel"
        prompt += ", or press 'k' to stop alert): "

        try:
            response = input(prompt).strip()
            # Stop alert and sound when user provides response
            stop_alert_flag.set()
            stop_sound()
        except (EOFError, KeyboardInterrupt):
            stop_alert_flag.set()
            stop_sound()
            return ("Witness skipped.", timer_end_time)

        if response.lower() == safe_word.lower():
            return ("Witness skipped.", timer_end_time)
        if response.lower() == 'k':
            stop_sound()
            console.print("[yellow]Sound stopped.[/yellow]")
            continue  # Let user try again to enter witness response
        if response:
            return (response, timer_end_time)
        # Allow empty response if no goal was set
        if goal is None:
            return ("Witness skipped.", timer_end_time)
        console.print(
            f"[red]Input cannot be empty. Please provide a description of your activity, or type '{safe_word}' to cancel.[/red]")
