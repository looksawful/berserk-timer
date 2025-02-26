import sys
import time
import threading
import select
import shutil
from typing import Callable, Dict
from rich.console import Console
from rich.text import Text
from .logger import view_today_log, delete_all_logs

console = Console()

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
    exit_flag = False
    suspend_display = threading.Event()

    def pause_action() -> None:
        timer.pause()
        console.print("[yellow]Timer paused. Press 'r' to resume.[/yellow]")

    def resume_action() -> None:
        timer.resume()
        console.print("[green]Timer resumed.[/green]")

    def stop_action() -> None:
        nonlocal exit_flag
        timer.stop()
        exit_flag = True
        console.print("[red]Timer stopped by user.[/red]")

    def zero_action() -> None:
        timer.zero()
        console.print("[blue]Timer zeroed.[/blue]")

    def restart_action() -> None:
        timer.restart()
        console.print("[cyan]Timer restarted.[/cyan]")

    def view_log_action() -> None:
        log_content = view_today_log()
        console.print("[magenta]Today's Witness Log:[/magenta]")
        console.print(log_content)

    def delete_logs_action() -> None:
        delete_all_logs()
        console.print("[bold red]All logs deleted.[/bold red]")

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
        timer.toggle_silent()  # Toggle silent mode in timer
        status = "enabled" if timer.is_silent() else "disabled"
        console.print(f"[yellow]Silent mode {status}.[/yellow]")

    def set_goal_action() -> None:
        suspend_display.set()
        try:
            new_goal = input("\nEnter your goal: ")
            timer.set_goal(new_goal)
            console.print(f"[blue]Goal set to: {new_goal}[/blue]")
        finally:
            suspend_display.clear()

    commands: Dict[str, Callable[[], None]] = {
        'p': pause_action,
        'r': resume_action,
        'q': stop_action,
        'z': zero_action,
        'n': restart_action,
        'v': view_log_action,
        'd': delete_logs_action,
        'u': update_duration_action,
        'g': set_goal_action,
        'm': set_mute_action
    }

    def keyboard_listener() -> None:
        nonlocal exit_flag
        while timer.is_running() and not exit_flag:
            if kbhit():
                try:
                    key = getch().lower()
                except UnicodeDecodeError:
                    continue
                if key in commands:
                    commands[key]()
                    if key in ('q', 'z'):
                        break
                else:
                    console.print(
                        "\n[red]Unknown command. Press (p, r, q, z, n, v, d, u, g, m) only.[/red]")
            time.sleep(0.1)

    listener = threading.Thread(target=keyboard_listener, daemon=True)
    listener.start()
    while timer.is_running() and not exit_flag:
        if not suspend_display.is_set():
            width = shutil.get_terminal_size().columns
            msg = f"Time remaining: {timer.get_remaining_time_str()}  (p: pause, r: resume, q: quit, z: zero, n: restart, v: view log, d: delete logs, u: update duration, g: set goal, m: silent mode)"
            print(f"\r{msg.ljust(width)}", end="", flush=True)
        time.sleep(0.1)
    console.print()
    return exit_flag


def cli_witness_form(safe_word: str) -> str:
    while True:
        response = input(
            f"\nTimer finished. Please enter what you were doing (or type '{safe_word}' to cancel): ").strip()
        if response.lower() == safe_word.lower():
            return "Witness skipped."
        if response:
            return response
        console.print(
            f"[red]Input cannot be empty. Please provide a description of your activity, or type '{safe_word}' to cancel.[/red]")
